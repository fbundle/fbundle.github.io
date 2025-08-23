#!/usr/bin/env python3
"""
========================================
🚀 CURSOR AI SIGNATURE
========================================

Written by Cursor AI in 2025 🎯
Enhanced AI tools for PDF document description generation
Built with efficiency and clean architecture in mind

Visit: https://cursor.com (the AI-powered code editor that made this possible!)

========================================
AI TOOLS - PDF Document Processing
========================================

AI tools for generating descriptions of PDF documents using the 
DeepSeek-R1-Distill-Qwen-1.5B model via transformers.

Key Features:
- Single document processing optimized for generate_text.py
- Memory-efficient model loading (load once, use many times)
- Automatic fallback to simple descriptions
- Real-time processing feedback with interactive output
- Clean thinking process removal from AI responses
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
            "device": DEVICE if torch.backends.mps.is_available() and DEVICE == "mps" else "cpu"
        }
except ImportError:
    # Fallback configuration if config file doesn't exist
    def get_ai_config():
        """Get AI configuration settings (fallback)."""
        return {
            "use_ai_model": True,
            "max_chars_per_doc": 1000,
            "device": "mps" if torch.backends.mps.is_available() else "cpu"
        }


class DocDescriptionModel:
    """
    A model class that loads the AI model once and provides methods for document processing.
    This prevents reloading the model for each document, making it much more efficient.
    """
    
    def __init__(self):
        self.model = None
        self.device = None
        self.cache_dir = None
        self.config = get_ai_config()
        self._load_model()
    
    def _load_model(self):
        """Load the AI model once during initialization."""
        if not self.config["use_ai_model"]:
            print("⚠ AI model disabled in configuration")
            return
        
        try:
            print("🔄 Initializing AI model for document processing...")
            
            # Set up device
            print(f"🔄 Setting up device: {self.config['device']}")
            self.device = torch.device(self.config["device"])
            print(f"✓ Using device: {self.device}")
            
            # Find cache directory
            print("🔄 Searching for model cache directory...")
            self.cache_dir = ""
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
                    self.cache_dir = cd
                    break
            
            if not self.cache_dir:
                raise RuntimeError("No cache directory found for models")
            print(f"✓ Found cache directory: {self.cache_dir}")
            
            # Load the model
            print("🔄 Loading AI model...")
            model_factory = get_model_factory()
            self.model = model_factory["deepseekr1_distill_qwen1p5b_transformers"](
                device=self.device, 
                cache_dir=self.cache_dir
            )
            print("✓ AI model loaded successfully")
            
        except Exception as e:
            print(f"✗ Failed to load AI model: {e}")
            print("⚠ Will use simple descriptions as fallback")
            self.model = None
    
    def get_ai_doc_description(self, text_content: str) -> str:
        """
        Generate AI description for a single PDF document using the pre-loaded model.
        
        Args:
            text_content: Text content extracted from a single PDF
            
        Returns:
            str: Brief description of the document (2-3 sentences)
        """
        if self.model is None:
            print("⚠ AI model not available, using simple description...")
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
        max_chars = self.config["max_chars_per_doc"]
        if len(text_content) > max_chars:
            print(f"⚠ Document too long ({len(text_content)} chars), truncating to {max_chars} chars...")
            text_content = text_content[:max_chars] + "..."
        
        print(f"✓ Prepared input ({len(text_content)} characters)")
        
        try:
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
            for text in self.model.chat(messages):
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
    
    def get_simple_doc_description(self, text_content: str) -> str:
        """
        Generate a simple description without using AI.
        
        Args:
            text_content: Text content from the document
            
        Returns:
            str: Simple description based on content analysis
        """
        return _generate_simple_doc_description(text_content)


def get_doc_description_model() -> DocDescriptionModel:
    """
    Factory function to create a DocDescriptionModel instance.
    
    Returns:
        DocDescriptionModel: A model instance with the AI model pre-loaded
    """
    return DocDescriptionModel()


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
