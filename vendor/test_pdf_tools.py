#!/usr/bin/env python3
"""
Test script for cursor_ai_pdf_tools
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cursor_ai_pdf_tools import get_pdf_desc

def test_pdf_descriptions():
    """Test the get_pdf_desc function with various PDF files."""
    
    test_files = [
        "ma5204_notes.pdf",
        "ma4261_hw1.pdf", 
        "ma5205_notes.pdf",
        "fyp.pdf",
        "mapf-gp.pdf",
        "paxos-algorithm.pdf"
    ]
    
    base_path = "../docs/assets/public_doc"
    
    print("Testing PDF Description Generation:")
    print("=" * 50)
    
    for filename in test_files:
        file_path = os.path.join(base_path, filename)
        if os.path.exists(file_path):
            try:
                description = get_pdf_desc(file_path)
                print(f"✓ {filename}: {description}")
            except Exception as e:
                print(f"✗ {filename}: Error - {e}")
        else:
            print(f"✗ {filename}: File not found")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_pdf_descriptions()
