#!/usr/bin/env python3
"""
AI Tools for PDF Description Generation

This module provides functions to generate accurate descriptions of PDF documents
using OpenAI's GPT models. It extracts key information and creates concise,
informative summaries.
"""

import os
import json
import logging
from typing import Dict, Tuple, Optional
import openai
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # Default to GPT-4o-mini for cost efficiency

def get_ai_description(text_dict: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
    """
    Generate AI-powered descriptions for PDF documents based on extracted text.
    
    Args:
        text_dict: Dictionary mapping PDF file paths to extracted text content
        
    Returns:
        Tuple of (overall_summary, individual_descriptions)
        - overall_summary: A brief summary of all documents
        - individual_descriptions: Dictionary mapping PDF paths to descriptions
    """
    
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        return "", {}
    
    try:
        openai.api_key = OPENAI_API_KEY
        
        # Generate individual descriptions for each PDF
        individual_descriptions = {}
        for pdf_path, text_content in text_dict.items():
            if not text_content.strip():
                individual_descriptions[pdf_path] = "No text content available"
                continue
                
            description = _generate_single_description(pdf_path, text_content)
            individual_descriptions[pdf_path] = description
        
        # Generate overall summary
        overall_summary = _generate_overall_summary(text_dict, individual_descriptions)
        
        return overall_summary, individual_descriptions
        
    except Exception as e:
        logger.error(f"Error generating AI descriptions: {e}")
        return "", {}

def _generate_single_description(pdf_path: str, text_content: str) -> str:
    """
    Generate a description for a single PDF document.
    
    Args:
        pdf_path: Path to the PDF file
        pdf_name: Name of the PDF file
        text_content: Extracted text content
        
    Returns:
        Concise description of the document
    """
    
    pdf_name = Path(pdf_path).stem
    
    # Truncate text if too long (to stay within token limits)
    max_chars = 8000  # Conservative limit
    if len(text_content) > max_chars:
        text_content = text_content[:max_chars] + "... [truncated]"
    
    prompt = f"""
You are an expert academic document analyzer. Your task is to provide a concise, accurate description of the following document.

Document: {pdf_name}
Content: {text_content}

Please provide a description that:
1. Identifies the main topic/subject area
2. Specifies the document type (e.g., homework, notes, paper, assignment)
3. Mentions key mathematical concepts, theorems, or topics covered
4. Is concise (2-3 sentences maximum)
5. Is accurate and factual based on the content provided

Format your response as a single, clear sentence that captures the essence of the document.
"""
    
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a precise academic document analyzer. Provide accurate, concise descriptions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.1,  # Low temperature for consistency
            timeout=30
        )
        
        description = response.choices[0].message.content.strip()
        return description
        
    except Exception as e:
        logger.error(f"Error generating description for {pdf_name}: {e}")
        return f"Error generating description: {str(e)}"

def _generate_overall_summary(text_dict: Dict[str, str], descriptions: Dict[str, str]) -> str:
    """
    Generate an overall summary of all documents.
    
    Args:
        text_dict: Dictionary mapping PDF paths to text content
        descriptions: Dictionary mapping PDF paths to individual descriptions
        
    Returns:
        Overall summary of the document collection
    """
    
    if not descriptions:
        return "No documents available for summary."
    
    # Create a summary of what we have
    doc_count = len(text_dict)
    doc_names = [Path(path).stem for path in text_dict.keys()]
    
    # Group by common themes if possible
    summary_parts = [
        f"This collection contains {doc_count} documents:",
        ", ".join(doc_names[:5])  # Show first 5 names
    ]
    
    if doc_count > 5:
        summary_parts.append(f"and {doc_count - 5} more documents.")
    
    return " ".join(summary_parts)

def test_ai_connection() -> bool:
    """
    Test the connection to OpenAI API.
    
    Returns:
        True if connection successful, False otherwise
    """
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not set")
        return False
    
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5,
            timeout=10
        )
        logger.info("OpenAI API connection successful")
        return True
    except Exception as e:
        logger.error(f"OpenAI API connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test the module
    print("Testing AI Tools module...")
    if test_ai_connection():
        print("✓ OpenAI API connection successful")
    else:
        print("✗ OpenAI API connection failed")
