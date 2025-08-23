from typing import *
import os
import sys
import time
import torch
from threading import Thread
import pydantic
import importlib
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from llama_cpp import Llama


def print_and_flush(*args, **kwargs):
    print(*args, **kwargs, flush=True)

ROLE_USER = "user"
ROLE_SYSTEM = "system"
ROLE_ASSISTANT = "assistant"

class Message(pydantic.BaseModel):
    role: str
    content: str

class Model:
    def chat(self, message_list: list[Message]) -> Iterator[str]:
        raise NotImplemented

class TransformersModel(Model):
    def __init__(
        self,
        model_path: str,
        dtype: torch.dtype,
        device: torch.device,
        tokenizer_kwargs: dict | None = None,
        model_kwargs: dict | None = None,
        generate_kwargs: dict | None = None,
    ):
        super().__init__()
        self.dtype = dtype
        self.device = device
        
        if tokenizer_kwargs is None:
            tokenizer_kwargs = {}
        if model_kwargs is None:
            model_kwargs = {}
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, **tokenizer_kwargs)
        self.model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=model_path,
            **model_kwargs,
        ).eval().to(self.dtype).to(self.device)
        
        self.generate_kwargs = {}
        if generate_kwargs is not None:
            self.generate_kwargs.update(generate_kwargs)

    def _generate(self, message_list: list[Message], text_streamer: TextIteratorStreamer):
        input_text = self.tokenizer.apply_chat_template(
            conversation=[message.model_dump() for message in message_list],
            tokenize=False,
            add_generation_prompt=True,
        )
        model_inputs = self.tokenizer(input_text, return_tensors="pt").to(self.dtype).to(self.device)
        self.model.generate(
            **model_inputs,
            streamer=text_streamer,
            **self.generate_kwargs,
        )

    def chat(self, message_list: list[Message]) -> Iterator[str]:
        text_streamer = TextIteratorStreamer(self.tokenizer,
            skip_prompt=True, # skip the prompt, stream the output only
            skip_special_tokens=True, # pass into tokenizer.decode, skip EOS for example
        )
        thread = Thread(target=TransformersModel._generate, args=(self, message_list, text_streamer))
        thread.start()
        def streamer() -> Iterator[str]:
            yield from text_streamer
            thread.join()
            
        return streamer()

class LlamaCPPModel(Model):
    def __init__(
            self,
            repo_id: str,
            filename: str,
            model_kwargs: dict | None = None,
            create_chat_completion_kwargs: dict | None = None,
        ):
        super().__init__()
        if model_kwargs is None:
            model_kwargs = {}
        self.llm = Llama.from_pretrained(
            repo_id=repo_id,
            filename=filename,
            **model_kwargs,
        )
        self.create_chat_completion_kwargs = {}
        if create_chat_completion_kwargs is not None:
            self.create_chat_completion_kwargs.update(create_chat_completion_kwargs)
    
    def chat(self, message_list: list[Message]) -> Iterator[str]:
        response = self.llm.create_chat_completion(
            messages=[message.model_dump() for message in message_list],
            stream=True,
            stop=["<|User|>"],
            **self.create_chat_completion_kwargs,
        )
        def streamer():
            for chunk in response:
                yield chunk["choices"][0]["delta"].get("content", "")

        return streamer()

class Conversation:
    def __init__(self, conversation_path: str = ""):
        self.conversation_path = conversation_path
        self.message_list = []
        if len(conversation_path) > 0:
            if not os.path.exists(self.conversation_path):
                parent_path = os.path.dirname(self.conversation_path)
                if not os.path.exists(parent_path):
                    os.makedirs(parent_path)
            else:
                for line in open(self.conversation_path):
                    line = line.strip()
                    if len(line) == 0:
                        continue
                    message = Message.model_validate_json(line)
                    self.message_list.append(message)
    
    def extend(self, *message_list: Message):
        self.message_list.extend(message_list)
        if len(conversation_path) > 0:
            with open(self.conversation_path, "a") as f:
                for message in message_list:
                    f.write(message.model_dump_json() + "\n")

def parse_message(text: str) -> Message:
    """
    prompt should be something like
    (system prompt) /system you are an AI agent
    (user prompt) hello, please help, what is an R module in math
    """
    text = text.strip()
    if len(text) == 0:
        return None

    prefix = text.split(maxsplit=1)[0].lower()

    if prefix == "/system":
        return Message(
            role=ROLE_SYSTEM,
            content=text.lstrip("/system")
        )
    else:
        return Message(
            role=ROLE_USER,
            content=text,
        )

def get_model_factory() -> dict[str, Callable[[], Model]]:
    def get_openai_gpt_oss_20b_transformers_model(device: torch.device | None, cache_dir: str):
        return TransformersModel(
            model_path="openai/gpt-oss-20b",
            dtype=torch.bfloat16,
            device=device,
            model_kwargs={
                "cache_dir": cache_dir,
            },
        )

    def get_deepseekr1_distill_qwen1p5b_transformers_model(device: torch.device | None, cache_dir: str):
        return TransformersModel(
            model_path="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
            dtype=torch.bfloat16,
            device=device,
            model_kwargs={
                "cache_dir": cache_dir,
            },
            generate_kwargs={
                "max_new_tokens": 131072,
                "temperature": 0.6,
                "top_p": 0.95,
            },
        )

    def get_deepseekr1_distill_qwen1p5b_llamacpp_model(device: torch.device | None, cache_dir: str):
        return LlamaCPPModel(
            repo_id="lmstudio-community/DeepSeek-R1-Distill-Qwen-1.5B-GGUF",
            filename="DeepSeek-R1-Distill-Qwen-1.5B-Q4_K_M.gguf",
            model_kwargs={
                "verbose": False,
                "n_gpu_layers": -1,
                "n_ctx": 4096, 
                "cache_dir": cache_dir,
            },
            create_chat_completion_kwargs={
                "max_tokens": 131072,
                "temperature": 0.6,
                "top_p": 0.95,
            },
        )
    def get_deepseekr1_distill_qwen32b_llamacpp_model(device: torch.device | None, cache_dir: str):
        return LlamaCPPModel(
            repo_id="bartowski/DeepSeek-R1-Distill-Qwen-32B-GGUF",
            filename="DeepSeek-R1-Distill-Qwen-32B-Q4_K_M.gguf",
            model_kwargs={
                "verbose": False,
                "n_gpu_layers": -1,
                "n_ctx": 4096,
                "cache_dir": cache_dir,
            },
            create_chat_completion_kwargs={
                "temperature": 0.6,
                "top_p": 0.95,
            },
        )
    def get_deepseekr1_distill_qwen7b_llamacpp_model(device: torch.device | None, cache_dir: str):
        return LlamaCPPModel(
            repo_id="bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF",
            filename="DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf",
            model_kwargs={
                "verbose": False,
                "n_gpu_layers": -1,
                "n_ctx": 4096,
                "cache_dir": cache_dir,
            },
            create_chat_completion_kwargs={
                "temperature": 0.6,
                "top_p": 0.95,
            },
        )

    def get_qwq_32b_llamacpp_model(device: torch.device | None, cache_dir: str):
        return LlamaCPPModel(
            repo_id="bartowski/Qwen_QwQ-32B-GGUF",
            filename="Qwen_QwQ-32B-IQ2_XXS.gguf",
            model_kwargs={
                "verbose": False,
                "n_gpu_layers": -1,
                "n_ctx": 4096,
                "cache_dir": cache_dir,
            },
            create_chat_completion_kwargs={
                "temperature": 0.6,
                "top_p": 0.95,
            },
        )

    def get_gemma_3_27b_llamacpp_model(device: torch.device | None, cache_dir: str):
        return LlamaCPPModel(
            repo_id="bartowski/google_gemma-3-27b-it-GGUF",
            filename="google_gemma-3-27b-it-IQ2_XS.gguf",
            model_kwargs={
                "verbose": False,
                "n_gpu_layers": -1,
                "n_ctx": 4096,
                "cache_dir": cache_dir,
            },
            create_chat_completion_kwargs={
                "temperature": 0.6,
                "top_p": 0.95,
            },
        )
    def get_qwq_32b_transformers_model(device: torch.device | None, cache_dir: str):
        return TransformersModel(
            model_path="Qwen/QwQ-32B",
            dtype=torch.bfloat16,
            device=device,
            model_kwargs={
                "cache_dir": cache_dir,
            },
        )
    
    def get_qwen3_30b_llamacpp_model(device: torch.device | None, cache_dir: str):
        return LlamaCPPModel(
            repo_id="bartowski/Qwen_Qwen3-30B-A3B-GGUF",
            filename="Qwen_Qwen3-30B-A3B-Q6_K_L.gguf",
            model_kwargs={
                "verbose": False,
                "n_gpu_layers": -1,
                "n_ctx": 4096,
                "cache_dir": cache_dir,
            },
            create_chat_completion_kwargs={
                "temperature": 0.6,
                "top_p": 0.95,
            },
        )
    

    return {
        "deepseekr1_distill_qwen1p5b_transformers": get_deepseekr1_distill_qwen1p5b_transformers_model,
        "deepseekr1_distill_qwen1p5b_llamacpp": get_deepseekr1_distill_qwen1p5b_llamacpp_model,
        "deepseekr1_distill_qwen32b_llamacpp": get_deepseekr1_distill_qwen32b_llamacpp_model,
        "deepseekr1_distill_qwen7b_llamacpp": get_deepseekr1_distill_qwen7b_llamacpp_model,
        "qwq_32b_transformers": get_qwq_32b_transformers_model,
        "qwq_32b_llamacpp": get_qwq_32b_llamacpp_model,
        "gemma_3_27b_llamacpp": get_gemma_3_27b_llamacpp_model,
        "qwen3_30b_llamacpp": get_qwen3_30b_llamacpp_model,
        "gpt_oss_20b_transformers": get_openai_gpt_oss_20b_transformers_model,
    }

def get_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--list_model", help="list all models", default=False, action='store_true')
    parser.add_argument("--model", type=str, help="model name", default="deepseekr1_distill_qwen1p5b_transformers")
    parser.add_argument("--device", type=str, help="device", default="mps")
    parser.add_argument("--conversation", type=str, help="conversation.json", default="")
    parser.add_argument("--cache", type=str, help="cache dir", default="")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()
    model_factory = get_model_factory()

    if args.list_model:
        print("list of models:")
        for model_name in model_factory.keys():
            print(f"\t{model_name}")
        exit()

    model_name = args.model
    device = torch.device(args.device)
    conversation_path = args.conversation
    cache_dir = args.cache

    
    if len(cache_dir) == 0:
        cache_dir_list = [
            "/Users/khanh/vault/downloads/model",
            "/home/khanh/Downloads/model/"
        ]
        for cd in cache_dir_list:
            if os.path.exists(cd):
                cache_dir = cd
                break
    
    assert len(cache_dir) > 0

    model = model_factory[model_name](device=device, cache_dir=cache_dir)
    conversation = Conversation(conversation_path=conversation_path)

    while True:
        message = parse_message(input("prompt: "))
        if message is not None:
            conversation.extend(message)
        if conversation.message_list[-1].role == ROLE_SYSTEM:
            continue

        print_and_flush(f"assistant: ", end="")
        try:
            token_count = 0
            t1 = time.perf_counter()

            response = ""
            for text in model.chat(conversation.message_list):
                print_and_flush(text, end="")
                response += text
                token_count += 1

        except KeyboardInterrupt:
            pass
        finally:
            conversation.extend(Message(
                role=ROLE_ASSISTANT,
                content=response,
            ))

            dur = time.perf_counter() - t1
            print(f"\ntotal_time: {int(round(dur))}s num_tokens: {token_count} token_per_sec: {token_count / dur}", file=sys.stderr)
            pass
        print_and_flush()


    
