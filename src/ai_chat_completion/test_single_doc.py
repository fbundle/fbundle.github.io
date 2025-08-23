#!/usr/bin/env python3
"""
Simple test script for single document AI processing.
"""

import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ai_chat_completion import ai_tools

def test_single_document():
    """Test the single document processing function."""
    print("Testing single document AI processing...")
    
    # Test with sample text content
    sample_text = """
    This document covers advanced linear algebra concepts including eigenvalues, eigenvectors, 
    and matrix diagonalization. The material focuses on spectral theory and its applications 
    to data science and machine learning algorithms. Topics include singular value decomposition, 
    principal component analysis, and their use in dimensionality reduction techniques.
    """
    
    print(f"Sample text length: {len(sample_text)} characters")
    
    try:
        # Test the AI function
        description = ai_tools.get_ai_doc_description(sample_text)
        print(f"\n✓ AI description generated: {description}")
        return True
    except Exception as e:
        print(f"✗ AI function failed: {e}")
        return False

def test_simple_fallback():
    """Test the simple fallback function."""
    print("\nTesting simple fallback function...")
    
    try:
        # Test with minimal content
        description = ai_tools._generate_simple_doc_description("test content")
        print(f"✓ Simple description: {description}")
        return True
    except Exception as e:
        print(f"✗ Simple function failed: {e}")
        return False

if __name__ == "__main__":
    print("Single Document AI Tools Test")
    print("=" * 50)
    
    # Test simple fallback first (fast)
    simple_success = test_simple_fallback()
    
    # Test AI function (slower)
    ai_success = test_single_document()
    
    print(f"\n{'='*50}")
    print("Test Results:")
    print(f"Simple fallback: {'✓' if simple_success else '✗'}")
    print(f"AI processing: {'✓' if ai_success else '✗'}")
    print(f"{'='*50}")
    
    if simple_success and ai_success:
        print("🎉 All tests passed!")
    else:
        print("⚠ Some tests failed. Check the output above.")
