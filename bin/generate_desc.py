#!/usr/bin/env python
import sys; import os;sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Set

import pydantic
from tqdm import tqdm

from src.util.pipe import ValueIter



from src.util.util import HtmlPath
from src.util.pdf_util import get_pdf_text
from src.util.ai_tools import DocDescriptionModel

import argparse
import time

class DocDescription(pydantic.BaseModel):
    name: str
    summary: str
    model: str





def generate_public_doc_desc(
        doc_htmldir: HtmlPath, desc_output_path: str,
):
    doc_dir = doc_htmldir.to_path()

    loaded: Set[tuple[str, str]] = set()
    if os.path.exists(desc_output_path):
        for line in open(desc_output_path):
            line = line.strip()
            if len(line) == 0:
                continue
            desc = DocDescription.model_validate_json(line)
            loaded.add((desc.name, desc.model))

    # model_name = "openai_gpt_oss_20b"
    # device_name_list = ["cuda:0", "cuda:1", "cuda:2", "cuda:3", "cuda:4", "cuda:5", "cuda:6", "cuda:7"]
    model_name = "deepseekr1_distill_qwen1p5b"
    device_name_list = ["mps"]

    name_list = list(os.listdir(doc_dir))
    unloaded_name_list = [name for name in name_list if (name, model_name) not in loaded]

    def make_generate_desc(i: int):
        device_name = device_name_list[i]
        model_wrapper = {
            "model": DocDescriptionModel(
                model_name=model_name,
                device_name=device_name,
            ),
        }

        def helper(name: str):
            try:
                path = f"{doc_dir}/{name}"
                text_content = get_pdf_text(path).strip()
                summary = model_wrapper["model"].get_ai_doc_description(text_content=text_content)

                desc = DocDescription(
                    name=name,
                    summary=summary,
                    model=model_name,
                )
                return desc
            except Exception as e:
                print(f"DEBUG: failed to generate description for {name}: {e}")
                # reset model
                del model_wrapper["model"]
                time.sleep(10) # wait for resource to be released
                model_wrapper["model"] = DocDescriptionModel(
                    model_name=model_name,
                    device_name=device_name,
                )
                return DocDescription(
                    name=name,
                    summary="",
                    model=model_name,
                )


        return helper

    parent_path = os.path.dirname(desc_output_path)
    if len(parent_path) > 0:
        os.makedirs(parent_path, exist_ok=True)
    for desc in tqdm(ValueIter(x_iter=unloaded_name_list).apply_parallel(
        make_map=make_generate_desc,
        nproc=len(device_name_list),
    ), desc="Generating descriptions", total=len(unloaded_name_list)):
        if len(desc.summary) == 0:
            continue
        with open(desc_output_path, "a") as f:
            f.write(desc.model_dump_json() + "\n")
        print(f"DEBUG: generated {desc.name} summary: {desc.summary}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html_root_dir", type=str)
    parser.add_argument("--doc_htmldir", type=str)
    parser.add_argument("--desc_output_path", type=str)
    args = parser.parse_args()


    DOC_HTMLDIR = HtmlPath(
        html_root_dir=args.html_root_dir,
        htmlpath=args.doc_htmldir,
    )

    generate_public_doc_desc(
        doc_htmldir=DOC_HTMLDIR,
        desc_output_path=args.desc_output_path,
    )