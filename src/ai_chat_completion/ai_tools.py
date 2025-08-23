#!/usr/bin/env python3
import os
import torch
from .llm_chat import get_model_factory, Message, ROLE_SYSTEM, ROLE_USER


class DocDescriptionModel:
    """
    A model class that loads the AI model once and provides methods for document processing.
    This prevents reloading the model for each document, making it much more efficient.
    """

    def __init__(self,
                 model_name: str = "gpt_oss_20b_transformers",
                 device: torch.device | None = torch.device("cpu" if not torch.cuda.is_available() else "cuda:0"),
                 cache_dir: str | None = "tmp",
                 max_input_char: int = 10000,
                 max_output_char: int = 300,
                 max_text_output_count: int = 10000,
                 ):
        self.max_input_char = max_input_char
        self.max_output_chars = max_output_char
        self.max_text_output_count = max_text_output_count
        model_factory = get_model_factory()
        self.model = model_factory[model_name](
            device=device,
            cache_dir=cache_dir
        )

        prompt_file = os.path.join(os.path.dirname(__file__), "ai_single_doc_prompt.txt")
        with open(prompt_file, 'r') as f:
            self.prompt = f.read()

    def get_ai_doc_description(self, text_content: str) -> str:
        if len(text_content) > self.max_input_char:
            text_content = text_content[:self.max_input_char]

        messages = [
            Message(role=ROLE_SYSTEM, content=self.prompt),
            Message(role=ROLE_USER, content=f"Please analyze this document:\n\n{text_content}")
        ]

        print(f"\n{'=' * 50}")
        print("AI is generating document description...")
        print(f"Document length: {len(text_content)} characters")
        print(f"{'=' * 50}")

        response = ""
        for i, text in enumerate(self.model.chat(messages)):
            if i >= self.max_text_output_count:
                raise Exception("AI output limit exceeded")
            print(text, end="", flush=True)  # Print each token as it's generated
            response += text
        print()  # New line after completion

        print(f"{'=' * 50}")
        print("AI generation completed!")
        print(f"{'=' * 50}")

        # Parse the response - for single document, we expect just the description
        print("Parsing AI response...")

        # Clean up the response and extract the description
        response = response.strip()

        # Remove any markdown formatting or extra text
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        # Remove thinking process text (common patterns)
        thinking_patterns = [
            "Alright,",
            "Let me",
            "I need to",
            "First,",
            "So,",
            "Putting it all together,",
            "In conclusion,",
            "<think>",
            "</think>",
            "Next,",
            "I should",
            "I'll",
            "The user",
            "This document",
            "The document"
        ]

        # More aggressive pattern removal
        for pattern in thinking_patterns:
            if pattern in response:
                # Find the start of thinking text and remove it
                parts = response.split(pattern)
                if len(parts) > 1:
                    # Keep only the last part (the actual description)
                    response = parts[-1].strip()
                    # Continue checking for more patterns
                    continue

        # Additional cleanup: remove any remaining thinking text
        lines = response.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            # Skip lines that look like thinking process
            if any(skip in line.lower() for skip in ['think', 'user', 'document', 'should', 'need to']):
                continue
            if line and len(line) > 10:  # Only keep substantial lines
                clean_lines.append(line)

        if clean_lines:
            response = ' '.join(clean_lines)

        # If response is too long, truncate it
        if len(response) > self.max_output_chars:
            response = "..." + response[-self.max_output_chars:]

        print("✓ Successfully generated document description")

        # Display final result
        print(f"\n{'=' * 50}")
        print("🎉 SINGLE DOCUMENT DESCRIPTION COMPLETED!")
        print(f"{'=' * 50}")
        print(f"Description: {response}")
        print(f"{'=' * 50}")

        return response


def get_doc_description_model() -> DocDescriptionModel:
    return DocDescriptionModel()
