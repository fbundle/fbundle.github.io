#!/usr/bin/env python3
"""
Test script to demonstrate AI tools configuration and usage.
"""

import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ai_chat_completion import ai_tools

def test_configuration():
    """Test the configuration system."""
    print("=== Testing Configuration ===")
    
    # Get current configuration
    config = ai_tools.get_ai_config()
    print(f"Current config: {config}")
    
    # Test with sample data
    sample_texts = {
        "docs/public_doc/calculus.pdf": "This document covers fundamental calculus concepts including limits, derivatives, and integrals...",
        "docs/public_doc/linear_algebra.pdf": "Linear algebra fundamentals covering vectors, matrices, and linear transformations...",
        "docs/public_doc/optimization.pdf": "Optimization techniques including gradient descent, linear programming, and convex optimization..."
    }
    
    print(f"\nSample data: {len(sample_texts)} documents")
    
    return sample_texts

def test_simple_description(sample_texts):
    """Test the simple description function."""
    print("\n=== Testing Simple Description ===")
    
    try:
        summary, descriptions = ai_tools.get_ai_description_simple(sample_texts)
        print(f"Summary: {summary}")
        print("Descriptions:")
        for path, desc in descriptions.items():
            print(f"  {path}: {desc}")
        return True
    except Exception as e:
        print(f"Simple description failed: {e}")
        return False

def test_ai_description(sample_texts):
    """Test the AI description function."""
    print("\n=== Testing AI Description ===")
    
    try:
        summary, descriptions = ai_tools.get_ai_description(sample_texts)
        print(f"Summary: {summary}")
        print("Descriptions:")
        for path, desc in descriptions.items():
            print(f"  {path}: {desc}")
        return True
    except Exception as e:
        print(f"AI description failed: {e}")
        print("This is expected if the model is not available or if there are memory issues")
        return False

def test_batched_description(sample_texts):
    """Test the batched description function."""
    print("\n=== Testing Batched Description ===")
    
    try:
        summary, descriptions = ai_tools.get_ai_description_batched(sample_texts, batch_size=2)
        print(f"Summary: {summary}")
        print("Descriptions:")
        for path, desc in descriptions.items():
            print(f"  {path}: {desc}")
        return True
    except Exception as e:
        print(f"Batched description failed: {e}")
        print("This is expected if the model is not available or if there are memory issues")
        return False

def main():
    """Run all tests."""
    print("AI Tools Test Suite")
    print("=" * 50)
    
    # Test configuration
    sample_texts = test_configuration()
    
    # Test simple description (should always work)
    simple_success = test_simple_description(sample_texts)
    
    # Test AI description (may fail if model not available)
    ai_success = test_ai_description(sample_texts)
    
    # Test batched description (may fail if model not available)
    batched_success = test_batched_description(sample_texts)
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Simple description: {'✓' if simple_success else '✗'}")
    print(f"AI description: {'✓' if ai_success else '✗'}")
    print(f"Batched description: {'✓' if batched_success else '✗'}")
    
    if simple_success:
        print("\n✓ Basic functionality is working!")
    else:
        print("\n✗ Basic functionality has issues!")
    
    if ai_success:
        print("✓ AI model is working!")
    else:
        print("✗ AI model is not available or has issues!")
        print("  You can still use simple descriptions or check the configuration.")
    
    print("\nTo modify behavior, edit src/ai_chat_completion/ai_config.py")

if __name__ == "__main__":
    main()
