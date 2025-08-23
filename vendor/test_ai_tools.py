#!/usr/bin/env python3
"""
Test script for AI Tools module

This script tests the PDF description generation functionality.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the module
sys.path.append(str(Path(__file__).parent))

from ai_tools import get_ai_description, test_ai_connection
from config import validate_config, print_config

def test_with_sample_data():
    """Test the AI description generation with sample PDF text data."""
    
    # Sample text data that might come from PDFs
    sample_texts = {
        "/path/to/ma5204_hw1.pdf": """
        MA5204 Homework 1
        Due: September 15, 2024
        
        Problem 1: Let V be a vector space over a field F. Prove that if v1, v2, ..., vn are linearly independent vectors in V, then any subset of these vectors is also linearly independent.
        
        Problem 2: Consider the matrix A = [1 2; 3 4]. Find the eigenvalues and eigenvectors of A.
        
        Problem 3: Let T: V -> W be a linear transformation. Show that ker(T) is a subspace of V.
        """,
        
        "/path/to/complex_analysis_ahlfors.pdf": """
        Complex Analysis - Ahlfors
        
        Chapter 1: Complex Numbers and Functions
        
        We begin with the study of complex numbers, which form a field that extends the real numbers. A complex number z = x + iy where x, y are real numbers and i² = -1.
        
        The Cauchy-Riemann equations are fundamental to complex analysis:
        ∂u/∂x = ∂v/∂y
        ∂u/∂y = -∂v/∂x
        
        These equations must be satisfied for a function f(z) = u(x,y) + iv(x,y) to be differentiable.
        """,
        
        "/path/to/algebraic_geometry_hartshorne.pdf": """
        Algebraic Geometry - Robin Hartshorne
        
        Chapter 2: Schemes
        
        A scheme is a locally ringed space (X, OX) which is locally isomorphic to Spec A for some commutative ring A. The structure sheaf OX gives us a way to define regular functions on X.
        
        Key concepts include:
        - Affine schemes
        - Sheaves and presheaves
        - Morphisms of schemes
        - Projective schemes
        
        The Zariski topology plays a crucial role in algebraic geometry.
        """
    }
    
    print("Testing AI description generation with sample data...")
    print("=" * 60)
    
    try:
        summary, descriptions = get_ai_description(sample_texts)
        
        print(f"\nOverall Summary: {summary}")
        print("\nIndividual Descriptions:")
        print("-" * 40)
        
        for pdf_path, description in descriptions.items():
            pdf_name = Path(pdf_path).name
            print(f"{pdf_name}: {description}")
            
    except Exception as e:
        print(f"Error during testing: {e}")

def main():
    """Main test function."""
    print("AI Tools Module Test Suite")
    print("=" * 40)
    
    # Test configuration
    print("\n1. Testing Configuration...")
    print_config()
    config_valid = validate_config()
    
    if not config_valid:
        print("\n❌ Configuration validation failed. Please fix the issues above.")
        return
    
    # Test API connection
    print("\n2. Testing OpenAI API Connection...")
    if test_ai_connection():
        print("✅ API connection successful")
    else:
        print("❌ API connection failed")
        print("   Please check your OPENAI_API_KEY and internet connection")
        return
    
    # Test with sample data
    print("\n3. Testing Description Generation...")
    test_with_sample_data()
    
    print("\n" + "=" * 40)
    print("Test suite completed!")

if __name__ == "__main__":
    main()
