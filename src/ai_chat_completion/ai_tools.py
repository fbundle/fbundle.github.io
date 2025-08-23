#!/usr/bin/env python3
"""
AI tools for generating descriptions of PDF documents using the 
DeepSeek-R1-Distill-Qwen-1.5B model via transformers.
"""

import json
import os
import torch
from typing import Dict, Tuple, Optional
from .llm_chat import get_model_factory, Message, ROLE_SYSTEM, ROLE_USER

# Configuration
try:
    from .ai_config import *
    def get_ai_config():
        """Get AI configuration settings from config file."""
        return {
            "use_ai_model": USE_AI_MODEL,
            "max_chars_per_doc": MAX_CHARS_PER_DOC,
            "max_total_input": MAX_TOTAL_INPUT,
            "fallback_threshold": FALLBACK_THRESHOLD,
            "batch_size": BATCH_SIZE,
            "device": DEVICE if torch.backends.mps.is_available() and DEVICE == "mps" else "cpu"
        }
except ImportError:
    # Fallback configuration if config file doesn't exist
    def get_ai_config():
        """Get AI configuration settings (fallback)."""
        return {
            "use_ai_model": True,
            "max_chars_per_doc": 500,
            "max_total_input": 6000,
            "fallback_threshold": 8000,
            "batch_size": 3,
            "device": "mps" if torch.backends.mps.is_available() else "cpu"
        }


def get_ai_description(text_dict: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
    """
    Generate AI descriptions for PDF documents using the prompt file.
    
    Args:
        text_dict: Dictionary mapping PDF paths to their text content
        
    Returns:
        Tuple of (summary, description) where:
        - summary: Overall summary of the collection
        - description: Dictionary mapping PDF paths to descriptions
    """
    
    # Check configuration
    print("🔄 Checking AI configuration...")
    config = get_ai_config()
    if not config["use_ai_model"]:
        print("⚠ AI model disabled in configuration, using simple descriptions...")
        return get_ai_description_simple(text_dict)
    print("✓ AI model enabled in configuration")

    # Read the prompt file
    print("🔄 Reading AI prompt template...")
    prompt_file = os.path.join(os.path.dirname(__file__), "ai_description_prompt.txt")
    with open(prompt_file, 'r') as f:
        prompt = f.read()
    print(f"✓ Loaded prompt template ({len(prompt)} characters)")
    
    # Prepare the input for the AI model with more aggressive truncation
    print("🔄 Preparing document input...")
    # Calculate how many characters we can use per document to stay within token limits
    max_chars_per_doc = config["max_chars_per_doc"]
    documents_info = "\n\n".join([
        f"Document: {path}\nContent: {text[:max_chars_per_doc]}..."
        for path, text in text_dict.items()
    ])
    print(f"✓ Prepared input for {len(text_dict)} documents")

    # Combine prompt with document information
    full_prompt = f"{prompt}\n\n## Documents to Analyze:\n\n{documents_info}"
    
    try:
        # Get the model (using configuration for device and cache directory)
        print(f"🔄 Setting up device: {config['device']}")
        device = torch.device(config["device"])
        print(f"✓ Using device: {device}")
        
        # Try to find cache directory
        print("🔄 Searching for model cache directory...")
        cache_dir = ""
        try:
            from .ai_config import CACHE_DIRS
            cache_dir_list = CACHE_DIRS
        except ImportError:
            cache_dir_list = [
                "/Users/khanh/vault/downloads/model",
                "/home/khanh/Downloads/model/"
            ]
        
        for cd in cache_dir_list:
            if os.path.exists(cd):
                cache_dir = cd
                break
        
        if not cache_dir:
            raise RuntimeError("No cache directory found for models")
        print(f"✓ Found cache directory: {cache_dir}")
        
        # Get the model with memory-efficient settings
        print("🔄 Loading AI model...")
        model_factory = get_model_factory()
        model = model_factory["deepseekr1_distill_qwen1p5b_transformers"](
            device=device, 
            cache_dir=cache_dir
        )
        print("✓ AI model loaded successfully")
        
        # Check if we have enough memory and truncate if necessary
        print("🔄 Checking input length and memory constraints...")
        total_input_length = len(prompt) + len(documents_info)
        if total_input_length > config["max_total_input"]:
            print(f"⚠ Warning: Input too long ({total_input_length} chars), truncating documents...")
            # Further truncate documents
            max_chars_per_doc = 150
            documents_info = "\n\n".join([
                f"Document: {path}\nContent: {text[:max_chars_per_doc]}..."
                for path, text in text_dict.items()
            ])
            print(f"✓ Truncated to {len(documents_info)} chars")
        else:
            print(f"✓ Input length ({total_input_length} chars) within limits")
        
        # If still too long, use simple approach
        if len(documents_info) > config["fallback_threshold"]:
            print("⚠ Input still too long, falling back to simple description generation...")
            return get_ai_description_simple(text_dict)
        
        # Create message list for the chat
        messages = [
            Message(role=ROLE_SYSTEM, content=prompt),
            Message(role=ROLE_USER, content=f"Please analyze these documents:\n\n{documents_info}")
        ]
        
        # Get response from the model with real-time output
        print(f"\n{'='*50}")
        print("AI is generating descriptions...")
        print(f"Input length: {len(documents_info)} characters")
        print(f"Processing {len(text_dict)} documents...")
        print(f"{'='*50}")
        
        response = ""
        for text in model.chat(messages):
            print(text, end="", flush=True)  # Print each token as it's generated
            response += text
        print()  # New line after completion
        
        print(f"{'='*50}")
        print("AI generation completed!")
        print(f"{'='*50}")
        
        # Parse the response (assuming it follows the expected format with "|||" separator)
        print("Parsing AI response...")
        parts = response.split("|||")
        if len(parts) >= 2:
            print("✓ Found response separator, extracting content...")
            # Extract summary from the first part
            summary = parts[0].strip()
            
            # Try to find JSON in the remaining parts
            json_part = None
            for part in parts[1:]:
                part = part.strip()
                if part.startswith('{') and part.endswith('}'):
                    json_part = part
                    break
            
            if json_part:
                try:
                    description = json.loads(json_part)
                    print("✓ Successfully parsed JSON response")
                    
                    # Display final results
                    print(f"\n{'='*50}")
                    print("🎉 AI DESCRIPTION GENERATION COMPLETED!")
                    print(f"{'='*50}")
                    print(f"Summary: {summary[:100]}{'...' if len(summary) > 100 else ''}")
                    print(f"Documents processed: {len(description)}")
                    print(f"{'='*50}")
                    
                    return summary, description
                except json.JSONDecodeError as e:
                    print(f"⚠ Warning: Failed to parse AI response as JSON: {e}")
                    print("Falling back to manual extraction...")
                    # Fallback: try to extract descriptions manually
                    return _extract_descriptions_fallback(json_part, text_dict)
            else:
                print("⚠ Warning: No JSON found in AI response parts")
                print("Falling back to manual extraction...")
                # Fallback: try to extract information from the full response
                return _extract_descriptions_fallback(response, text_dict)
        else:
            print("⚠ Warning: AI response doesn't contain expected '|||' separator")
            print("Falling back to manual extraction...")
            # Fallback: try to extract information from the full response
            return _extract_descriptions_fallback(response, text_dict)
            
    except Exception as e:
        print(f"Error in AI description generation: {e}")
        print("Falling back to simple description generation...")
        # Return simple descriptions if AI processing fails
        return get_ai_description_simple(text_dict)


def _extract_descriptions_fallback(response: str, text_dict: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
    """
    Fallback method to extract descriptions when the AI response format is unexpected.
    
    Args:
        response: The AI model's response
        text_dict: Original text dictionary
        
    Returns:
        Tuple of (summary, description)
    """
    try:
        print("🔄 Using fallback extraction method...")
        
        # Try to find JSON-like content in the response
        import re
        
        # Look for JSON patterns - more flexible matching
        json_pattern = r'\{[^{}]*"[^"]*"[^{}]*\}'
        json_matches = re.findall(json_pattern, response)
        
        if json_matches:
            print(f"✓ Found {len(json_matches)} potential JSON patterns")
            # Try to parse the largest JSON match
            largest_match = max(json_matches, key=len)
            try:
                description = json.loads(largest_match)
                # Extract summary from before the JSON
                summary_part = response.split(largest_match)[0].strip()
                summary = summary_part if summary_part else "AI-generated summary of the document collection."
                print("✓ Successfully extracted JSON and summary from fallback")
                return summary, description
            except json.JSONDecodeError:
                print("⚠ JSON parsing failed, trying alternative extraction...")
                pass
        
        # Try to extract a summary from the response
        print("🔄 Extracting summary from response text...")
        lines = response.split('\n')
        summary_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('{') and not line.startswith('```'):
                summary_lines.append(line)
                if len(' '.join(summary_lines)) > 100:  # Limit summary length
                    break
        
        if summary_lines:
            summary = ' '.join(summary_lines)
            print("✓ Extracted summary from response text")
        else:
            summary = "AI-generated summary of the document collection."
            print("✓ Using default summary")
        
        # Create descriptions based on file names and content hints
        print("🔄 Generating document descriptions...")
        description = {}
        for path in text_dict.keys():
            filename = os.path.basename(path)
            name_without_ext = filename.replace('.pdf', '')
            
            # Look for content hints in the AI response
            content_hint = ""
            if name_without_ext.lower() in response.lower():
                # Find sentences mentioning this document
                sentences = re.split(r'[.!?]+', response)
                for sentence in sentences:
                    if name_without_ext.lower() in sentence.lower():
                        content_hint = sentence.strip()
                        break
            
            if content_hint:
                description[path] = content_hint
            else:
                description[path] = f"Document about {name_without_ext.replace('_', ' ')}"
        
        print(f"✓ Generated {len(description)} document descriptions")
        return summary, description
        
    except Exception as e:
        print(f"✗ Fallback extraction also failed: {e}")
        return "", {}


def get_ai_description_simple(text_dict: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
    """
    Simplified version that doesn't require the AI model - useful for testing.
    
    Args:
        text_dict: Dictionary mapping PDF paths to their text content
        
    Returns:
        Tuple of (summary, description)
    """
    if not text_dict:
        return "", {}
    
    print("🔄 Generating simple descriptions...")
    
    # Create a simple summary
    doc_count = len(text_dict)
    summary = f"This collection contains {doc_count} academic and technical documents covering various mathematical and scientific topics."
    print(f"✓ Generated summary for {doc_count} documents")
    
    # Create simple descriptions based on filenames
    description = {}
    for path in text_dict.keys():
        filename = os.path.basename(path)
        name_without_ext = filename.replace('.pdf', '')
        # Convert filename to readable description
        readable_name = name_without_ext.replace('_', ' ').replace('-', ' ')
        description[path] = f"Document about {readable_name}"
    
    print(f"✓ Generated {len(description)} document descriptions")
    return summary, description


def get_ai_description_batched(text_dict: Dict[str, str], batch_size: Optional[int] = None) -> Tuple[str, Dict[str, str]]:
    """
    Generate AI descriptions for PDF documents in batches to avoid memory issues.
    
    Args:
        text_dict: Dictionary mapping PDF paths to their text content
        batch_size: Number of documents to process at once
        
    Returns:
        Tuple of (summary, description) where:
        - summary: Overall summary of the collection
        - description: Dictionary mapping PDF paths to descriptions
    """
    if not text_dict:
        return "", {}
    
    print(f"\n{'='*60}")
    print("🚀 STARTING BATCHED AI DESCRIPTION GENERATION")
    print(f"{'='*60}")
    print(f"Total documents: {len(text_dict)}")
    print(f"Batch size: {batch_size if batch_size else 'default'}")
    
    # Process documents in batches
    all_descriptions = {}
    batch_summaries = []
    
    # Use configuration batch size if none specified
    if batch_size is None:
        batch_size = get_ai_config()["batch_size"]
    
    # Convert to list for easier batching
    items = list(text_dict.items())
    
    for i in range(0, len(items), batch_size):
        batch_items = items[i:i + batch_size]
        batch_dict = dict(batch_items)
        
        print(f"\n{'='*50}")
        print(f"Processing batch {i//batch_size + 1}/{(len(items) + batch_size - 1)//batch_size} ({len(batch_dict)} documents)")
        print(f"Documents: {', '.join([os.path.basename(path) for path in batch_dict.keys()])}")
        print(f"{'='*50}")
        
        try:
            # Process this batch
            batch_summary, batch_descriptions = get_ai_description(batch_dict)
            all_descriptions.update(batch_descriptions)
            if batch_summary:
                batch_summaries.append(batch_summary)
            print(f"✓ Batch {i//batch_size + 1} completed successfully")
        except Exception as e:
            print(f"✗ Batch {i//batch_size + 1} failed: {e}")
            print("Falling back to simple descriptions for this batch...")
            # Fallback to simple descriptions for this batch
            batch_summary, batch_descriptions = get_ai_description_simple(batch_dict)
            all_descriptions.update(batch_descriptions)
            if batch_summary:
                batch_summaries.append(batch_summary)
            print(f"✓ Batch {i//batch_size + 1} completed with fallback")
    
    # Combine batch summaries into overall summary
    print(f"\n{'='*50}")
    print("🔄 Generating final summary...")
    print(f"{'='*50}")
    
    if batch_summaries:
        overall_summary = " ".join(batch_summaries)
        print("✓ Combined batch summaries into overall summary")
    else:
        overall_summary = f"Collection of {len(text_dict)} academic and technical documents."
        print("✓ Generated fallback summary")
    
    print(f"\n{'='*60}")
    print("🎉 BATCHED AI DESCRIPTION GENERATION COMPLETED!")
    print(f"{'='*60}")
    print(f"Final Results:")
    print(f"- Total documents processed: {len(all_descriptions)}")
    print(f"- Summary length: {len(overall_summary)} characters")
    print(f"- Batches processed: {(len(items) + batch_size - 1)//batch_size}")
    print(f"{'='*60}")
    
    return overall_summary, all_descriptions


def get_ai_doc_description(text_content: str) -> str:
    """
    Generate AI description for a single PDF document.
    This function is designed to be called by generate_text.py for each individual document.
    
    Args:
        text_content: Text content extracted from a single PDF
        
    Returns:
        str: Brief description of the document (2-3 sentences)
    """
    # Check configuration
    config = get_ai_config()
    if not config["use_ai_model"]:
        print("⚠ AI model disabled in configuration, using simple description...")
        return _generate_simple_doc_description(text_content)
    
    print("🔄 Processing single document with AI...")
    
    # Read the single document prompt file
    prompt_file = os.path.join(os.path.dirname(__file__), "ai_single_doc_prompt.txt")
    try:
        with open(prompt_file, 'r') as f:
            prompt = f.read()
        print(f"✓ Loaded single document prompt template ({len(prompt)} characters)")
    except FileNotFoundError:
        print("⚠ Single document prompt not found, using fallback...")
        return _generate_simple_doc_description(text_content)
    
    # Prepare the input for the AI model
    print("🔄 Preparing document input...")
    # Truncate if too long to avoid memory issues
    max_chars = config["max_chars_per_doc"]
    if len(text_content) > max_chars:
        print(f"⚠ Document too long ({len(text_content)} chars), truncating to {max_chars} chars...")
        text_content = text_content[:max_chars] + "..."
    
    print(f"✓ Prepared input ({len(text_content)} characters)")
    
    try:
        # Get the model
        print(f"🔄 Setting up device: {config['device']}")
        device = torch.device(config["device"])
        print(f"✓ Using device: {device}")
        
        # Try to find cache directory
        print("🔄 Searching for model cache directory...")
        cache_dir = ""
        try:
            from .ai_config import CACHE_DIRS
            cache_dir_list = CACHE_DIRS
        except ImportError:
            cache_dir_list = [
                "/Users/khanh/vault/downloads/model",
                "/home/khanh/Downloads/model/"
            ]
        
        for cd in cache_dir_list:
            if os.path.exists(cd):
                cache_dir = cd
                break
        
        if not cache_dir:
            raise RuntimeError("No cache directory found for models")
        print(f"✓ Found cache directory: {cache_dir}")
        
        # Load the model
        print("🔄 Loading AI model...")
        model_factory = get_model_factory()
        model = model_factory["deepseekr1_distill_qwen1p5b_transformers"](
            device=device, 
            cache_dir=cache_dir
        )
        print("✓ AI model loaded successfully")
        
        # Create message list for the chat
        messages = [
            Message(role=ROLE_SYSTEM, content=prompt),
            Message(role=ROLE_USER, content=f"Please analyze this document:\n\n{text_content}")
        ]
        
        # Get response from the model with real-time output
        print(f"\n{'='*50}")
        print("AI is generating document description...")
        print(f"Document length: {len(text_content)} characters")
        print(f"{'='*50}")
        
        response = ""
        for text in model.chat(messages):
            print(text, end="", flush=True)  # Print each token as it's generated
            response += text
        print()  # New line after completion
        
        print(f"{'='*50}")
        print("AI generation completed!")
        print(f"{'='*50}")
        
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
            "</think>"
        ]
        
        for pattern in thinking_patterns:
            if pattern in response:
                # Find the start of thinking text and remove it
                parts = response.split(pattern)
                if len(parts) > 1:
                    # Keep only the last part (the actual description)
                    response = parts[-1].strip()
                    break
        
        # If response is too long, truncate it
        if len(response) > 500:
            response = response[:500] + "..."
        
        print("✓ Successfully generated document description")
        
        # Display final result
        print(f"\n{'='*50}")
        print("🎉 SINGLE DOCUMENT DESCRIPTION COMPLETED!")
        print(f"{'='*50}")
        print(f"Description: {response[:100]}{'...' if len(response) > 100 else ''}")
        print(f"{'='*50}")
        
        return response
        
    except Exception as e:
        print(f"Error in AI description generation: {e}")
        print("Falling back to simple description generation...")
        return _generate_simple_doc_description(text_content)


def _generate_simple_doc_description(text_content: str) -> str:
    """
    Generate a simple description for a single document without using AI.
    
    Args:
        text_content: Text content from the document
        
    Returns:
        str: Simple description based on content analysis
    """
    print("🔄 Generating simple document description...")
    
    if not text_content or len(text_content.strip()) < 10:
        return "Document with minimal or no readable content."
    
    # Analyze the content to generate a simple description
    words = text_content.lower().split()
    
    # Look for common academic keywords
    academic_keywords = {
        'mathematics': ['math', 'mathematical', 'calculus', 'algebra', 'geometry', 'analysis', 'theorem', 'proof'],
        'computer_science': ['algorithm', 'programming', 'software', 'computer', 'data', 'network', 'system'],
        'physics': ['physics', 'physical', 'mechanics', 'quantum', 'energy', 'force', 'motion'],
        'engineering': ['engineering', 'design', 'construction', 'mechanical', 'electrical', 'civil'],
        'biology': ['biology', 'biological', 'cell', 'organism', 'genetic', 'evolution'],
        'chemistry': ['chemistry', 'chemical', 'molecule', 'reaction', 'organic', 'inorganic']
    }
    
    detected_topics = []
    for topic, keywords in academic_keywords.items():
        if any(keyword in words for keyword in keywords):
            detected_topics.append(topic.replace('_', ' '))
    
    if detected_topics:
        topics_str = ', '.join(detected_topics)
        return f"Academic document covering topics in {topics_str}."
    else:
        # Count words and provide generic description
        word_count = len(words)
        if word_count < 100:
            return "Short document with limited content."
        elif word_count < 500:
            return "Medium-length academic or technical document."
        else:
            return "Comprehensive academic or technical document with substantial content."


# Example usage and testing
if __name__ == "__main__":
    # Sample text dictionary for testing
    sample_texts = {
        "docs/public_doc/calculus.pdf": "This document covers fundamental calculus concepts including limits, derivatives, and integrals...",
        "docs/public_doc/linear_algebra.pdf": "Linear algebra fundamentals covering vectors, matrices, and linear transformations...",
        "docs/public_doc/optimization.pdf": "Optimization techniques including gradient descent, linear programming, and convex optimization..."
    }
    
    print("Testing AI description generation...")
    
    # Test the simple version first
    print("\n--- Simple Version ---")
    summary, descriptions = get_ai_description_simple(sample_texts)
    print("Summary:", summary)
    print("Descriptions:")
    for path, desc in descriptions.items():
        print(f"  {path}: {desc}")
    
    # Test the AI version
    print("\n--- AI Version ---")
    try:
        summary, descriptions = get_ai_description(sample_texts)
        print("Summary:", summary)
        print("Descriptions:")
        for path, desc in descriptions.items():
            print(f"  {path}: {desc}")
    except Exception as e:
        print(f"AI version failed: {e}")
        print("This is expected if the model is not available")
    
    # Test the batched version
    print("\n--- Batched AI Version ---")
    try:
        summary, descriptions = get_ai_description_batched(sample_texts, batch_size=2)
        print("Summary:", summary)
        print("Descriptions:")
        for path, desc in descriptions.items():
            print(f"  {path}: {desc}")
    except Exception as e:
        print(f"Batched AI version failed: {e}")
        print("This is expected if the model is not available")
