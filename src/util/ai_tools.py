#!/usr/bin/env python3
import os
import re
import string

from .llm_chat import get_model_factory, Message, ROLE_SYSTEM, ROLE_USER


def clean_text(doc: str) -> str:
    """
    Normalize and clean an English document string.
    """
    # Lowercase
    doc = doc.lower()

    # Remove non-ASCII characters (emoji, foreign symbols, etc.)
    doc = doc.encode("ascii", errors="ignore").decode()

    # Replace newlines and tabs with space
    doc = re.sub(r"[\r\n\t]+", " ", doc)

    # Remove punctuation
    doc = doc.translate(str.maketrans("", "", string.punctuation))

    # Normalize multiple spaces → single space
    doc = re.sub(r"\s+", " ", doc)

    # Trim leading/trailing spaces
    doc = doc.strip()

    return doc


class DocDescriptionModel:
    def __init__(
            self,
            model_name: str = "deepseekr1_distill_qwen1p5b",
            device_name: str = "mps",
    ):
        self.model = get_model_factory()[model_name](device_name, None)

        print(f"Using model in device: {self.model.model.device}")

        prompt_file = os.path.join(os.path.dirname(__file__), "doc_desc_prompt.txt")
        with open(prompt_file, 'r') as f:
            self.prompt = f.read()

    def get_ai_doc_description(self, text_content: str) -> str:
        text_content = clean_text(text_content)
        chunk = False
        if chunk: # don't need to chunk for mistral model
            words = text_content.split()
            if len(words) > 1000:
                words = words[:1000]
            text_content = " ".join(words)

        messages = [
            Message(role=ROLE_SYSTEM, content=self.prompt),
            Message(role=ROLE_USER, content=f"Please analyze this document:\n\n{text_content}")
        ]

        print(f"\n{'=' * 50}")
        print("AI is generating document description...")
        print(f"Document length: {len(text_content.split())} words")
        print(f"{'=' * 50}")

        response = ""
        for i, text in enumerate(self.model.chat(messages)):
            if i >= 10000:
                raise Exception("AI output limit exceeded - probably hallucinated")
            print(text, end="", flush=True)
            response += text
        print()

        print(f"{'=' * 50}")
        print("AI generation completed!")
        print(f"{'=' * 50}")


        response = clean_text(response)

        print("✓ Successfully generated document description")

        # Display final result
        print(f"\n{'=' * 50}")
        print("🎉 SINGLE DOCUMENT DESCRIPTION COMPLETED!")
        print(f"{'=' * 50}")
        print(f"Description: {response}")
        print(f"{'=' * 50}")

        return response

