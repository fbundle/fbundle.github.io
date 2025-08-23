#!/usr/bin/env python3
"""
Example usage of the AI Tools module

This script demonstrates how to use the PDF description generation functionality.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import the module
sys.path.append(str(Path(__file__).parent))

from ai_tools import get_ai_description

def main():
    """Demonstrate the AI tools functionality."""
    
    print("📚 AI Tools Example Usage")
    print("=" * 40)
    
    # Check if API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set your OpenAI API key first:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Sample PDF text data (simulating extracted content)
    sample_pdfs = {
        "/docs/ma5204_hw1.pdf": """
        MA5204 Linear Algebra Homework 1
        Due: September 15, 2024
        
        Problem 1: Let V be a vector space over a field F. Prove that if v1, v2, ..., vn are linearly independent vectors in V, then any subset of these vectors is also linearly independent.
        
        Problem 2: Consider the matrix A = [1 2; 3 4]. Find the eigenvalues and eigenvectors of A.
        
        Problem 3: Let T: V -> W be a linear transformation. Show that ker(T) is a subspace of V.
        
        Problem 4: Let A be an n×n matrix. Prove that if A² = A, then A is diagonalizable.
        """,
        
        "/docs/complex_analysis_ahlfors.pdf": """
        Complex Analysis - Lars Ahlfors
        
        Chapter 1: Complex Numbers and Functions
        
        We begin with the study of complex numbers, which form a field that extends the real numbers. A complex number z = x + iy where x, y are real numbers and i² = -1.
        
        The Cauchy-Riemann equations are fundamental to complex analysis:
        ∂u/∂x = ∂v/∂y
        ∂u/∂y = -∂v/∂x
        
        These equations must be satisfied for a function f(z) = u(x,y) + iv(x,y) to be differentiable.
        
        Chapter 2: Power Series and Elementary Functions
        
        The exponential function e^z is defined by the power series:
        e^z = 1 + z + z²/2! + z³/3! + ...
        """,
        
        "/docs/algebraic_geometry_hartshorne.pdf": """
        Algebraic Geometry - Robin Hartshorne
        
        Chapter 2: Schemes
        
        A scheme is a locally ringed space (X, OX) which is locally isomorphic to Spec A for some commutative ring A. The structure sheaf OX gives us a way to define regular functions on X.
        
        Key concepts include:
        - Affine schemes
        - Sheaves and presheaves
        - Morphisms of schemes
        - Projective schemes
        
        The Zariski topology plays a crucial role in algebraic geometry.
        
        Chapter 3: First Properties of Schemes
        
        We study various properties of schemes including:
        - Connectedness
        - Irreducibility
        - Dimension theory
        - Regular schemes
        """,
        
        "/docs/differential_forms_and_stoke_theorem.pdf": """
        Differential Forms and Stokes' Theorem
        
        This document covers the fundamental concepts of differential forms and their applications in calculus and geometry.
        
        Key topics include:
        - Exterior algebra and differential forms
        - Integration of differential forms
        - Stokes' theorem in various dimensions
        - Applications to vector calculus
        
        The document includes proofs of:
        - Green's theorem in the plane
        - Stokes' theorem for surfaces
        - The divergence theorem
        - General Stokes' theorem for manifolds
        """
    }
    
    print(f"📖 Processing {len(sample_pdfs)} sample PDF documents...")
    print()
    
    try:
        # Generate AI descriptions
        print("🤖 Generating AI descriptions...")
        summary, descriptions = get_ai_description(sample_pdfs)
        
        # Display results
        print("\n" + "=" * 60)
        print("📋 RESULTS")
        print("=" * 60)
        
        print(f"\n📊 Overall Summary:")
        print(f"   {summary}")
        
        print(f"\n📝 Individual Descriptions:")
        print("-" * 50)
        
        for pdf_path, description in descriptions.items():
            pdf_name = Path(pdf_path).name
            print(f"   {pdf_name}")
            print(f"   → {description}")
            print()
        
        print("=" * 60)
        print("✅ Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        print("   Please check your API key and internet connection")

if __name__ == "__main__":
    main()
