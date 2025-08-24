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


def parse_response(response: str):
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

    return response

class DocDescriptionModel:
    def __init__(
            self,
            model_name: str = "deepseekr1_distill_qwen1p5b",
            device_name: str = "mps",
    ):
        self.model = get_model_factory()[model_name](device_name, None)

        prompt_file = os.path.join(os.path.dirname(__file__), "doc_desc_prompt.txt")
        with open(prompt_file, 'r') as f:
            self.prompt = f.read()

    def get_ai_doc_description(self, text_content: str) -> str:
        text_content = clean_text(text_content)
        words = text_content.split()
        if len(words) > 5000:
            words = words[:5000]
        text_content = " ".join(words)

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
            if i >= 10000:
                raise Exception("AI output limit exceeded - probably hallucinated")
            print(text, end="", flush=True)
            response += text
        print()

        print(f"{'=' * 50}")
        print("AI generation completed!")
        print(f"{'=' * 50}")


        response = parse_response(response)

        print("✓ Successfully generated document description")

        # Display final result
        print(f"\n{'=' * 50}")
        print("🎉 SINGLE DOCUMENT DESCRIPTION COMPLETED!")
        print(f"{'=' * 50}")
        print(f"Description: {response}")
        print(f"{'=' * 50}")

        return response

