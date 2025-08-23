#!/usr/bin/env python3
"""
PDF Description Tools for Cursor AI Integration

This module provides functions to analyze PDF files and generate
concise descriptions of their content for academic document collections.
"""

import os
import re
from pathlib import Path
from typing import Optional

try:
    import pymupdf
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("Warning: PyMuPDF not available. PDF analysis will be limited.")


def get_pdf_desc(pdf_data: list) -> tuple[str, dict]:
    """
    Generate descriptions for multiple PDFs based on their text content and provide a summary.
    
    Args:
        pdf_data (list): List of tuples (pdf_path, pdf_text) where pdf_text is the extracted text content
        
    Returns:
        tuple: (summary_string, descriptions_dict) where descriptions_dict maps paths to descriptions
        
    Raises:
        Exception: If there's an error processing the PDF data
    """
    if not pdf_data:
        return "No PDF files found.", {}
    
    descriptions = {}
    total_files = len(pdf_data)
    categories = {}
    
    for pdf_path, pdf_text in pdf_data:
        try:
            # Generate description based on text content
            description = _generate_description_from_text(pdf_path, pdf_text)
            descriptions[pdf_path] = description
            
            # Categorize and count
            category = _categorize_document_from_text(pdf_path, pdf_text, description)
            categories[category] = categories.get(category, 0) + 1
                
        except Exception as e:
            print(f"Error analyzing PDF {pdf_path}: {e}")
            descriptions[pdf_path] = "Error reading file"
    
    # Generate summary
    summary = _generate_collection_summary_from_categories(categories, total_files)
    
    return summary, descriptions


def _analyze_pdf_content(pdf_path: str) -> str:
    """Analyze PDF content using PyMuPDF to generate description."""
    doc = pymupdf.Document(pdf_path)
    
    # Get metadata
    metadata = doc.metadata
    title = metadata.get('title', '').strip()
    author = metadata.get('author', '').strip()
    subject = metadata.get('subject', '').strip()
    
    # Extract text from first few pages
    text_content = ""
    max_pages = min(3, len(doc))  # Analyze first 3 pages max
    
    for page_num in range(max_pages):
        try:
            page_text = doc[page_num].get_text()
            text_content += page_text + " "
        except Exception:
            continue
    
    # Clean up text
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    # Generate description based on content analysis
    description = _generate_description_from_content(
        pdf_path, text_content, title, author, subject
    )
    
    doc.close()
    return description


def _generate_description_from_text(pdf_path: str, pdf_text: str) -> str:
    """Generate description based on PDF text content."""
    filename = os.path.basename(pdf_path)
    filename_lower = filename.lower()
    text_lower = pdf_text.lower()
    
    # Course code patterns
    course_patterns = {
        'ma4261': 'Real Analysis',
        'ma4271': 'Differential Equations',
        'ma5204': 'Commutative and Homological Algebra',
        'ma5205': 'Measure and Integral',
        'ma5209': 'Advanced Mathematics',
        'ma5210': 'Advanced Mathematics',
        'ma5211': 'Advanced Mathematics',
        'ma5216': 'Advanced Mathematics',
        'ma5232': 'Advanced Mathematics',
        'ma5259': 'Advanced Mathematics',
        'ma5271': 'Advanced Mathematics'
    }
    
    # Identify course code
    course_code = None
    course_topic = None
    for code, topic in course_patterns.items():
        if code in filename_lower:
            course_code = code.upper()
            course_topic = topic
            break
    
    # Determine document type
    doc_type = "Document"
    if any(keyword in filename_lower for keyword in ['hw', 'homework']):
        doc_type = "Homework assignment"
    elif 'notes' in filename_lower:
        doc_type = "Course notes"
    elif any(keyword in filename_lower for keyword in ['a', 'assignment']):
        doc_type = "Assignment"
    elif 'tut' in filename_lower:
        doc_type = "Tutorial materials"
    elif 'test' in filename_lower:
        doc_type = "Test materials"
    
    # Identify key topics from content
    topics = _identify_topics(pdf_text)
    
    # Generate description
    if course_code:
        if doc_type == "Homework assignment":
            return f"{doc_type} for {course_code} {course_topic} course"
        elif doc_type == "Course notes":
            return f"{doc_type} for {course_code} {course_topic} course"
        elif doc_type == "Assignment":
            return f"{doc_type} for {course_code} {course_topic} course"
        else:
            return f"{doc_type} for {course_code} {course_topic} course"
    else:
        # Handle non-course documents
        if 'fyp' in filename_lower:
            return "Final Year Project report and research findings"
        elif 'mapf' in filename_lower:
            return "Research on Multi-Agent Pathfinding using genetic programming"
        elif 'network' in filename_lower:
            return "Network Science assignment covering network analysis"
        elif 'paxos' in filename_lower:
            return "Documentation on Paxos consensus algorithm"
        elif 'pca' in filename_lower:
            return "Notes on Principal Component Analysis and applications"
        elif 'vitae' in filename_lower:
            return "Personal curriculum vitae and academic background"
        elif topics:
            return f"Notes on {topics[0]} covering {', '.join(topics[1:3])}"
        else:
            return "Academic document covering mathematical concepts"


def _generate_description_from_content(
    pdf_path: str, 
    text_content: str, 
    title: str, 
    author: str, 
    subject: str
) -> str:
    """Generate description based on analyzed content."""
    filename = os.path.basename(pdf_path)
    filename_lower = filename.lower()
    
    # Course code patterns
    course_patterns = {
        'ma4261': 'Real Analysis',
        'ma4271': 'Differential Equations',
        'ma5204': 'Commutative and Homological Algebra',
        'ma5205': 'Measure and Integral',
        'ma5209': 'Advanced Mathematics',
        'ma5210': 'Advanced Mathematics',
        'ma5211': 'Advanced Mathematics',
        'ma5216': 'Advanced Mathematics',
        'ma5232': 'Advanced Mathematics',
        'ma5259': 'Advanced Mathematics',
        'ma5271': 'Advanced Mathematics'
    }
    
    # Identify course code
    course_code = None
    course_topic = None
    for code, topic in course_patterns.items():
        if code in filename_lower:
            course_code = code.upper()
            course_topic = topic
            break
    
    # Determine document type
    doc_type = "Document"
    if any(keyword in filename_lower for keyword in ['hw', 'homework']):
        doc_type = "Homework assignment"
    elif 'notes' in filename_lower:
        doc_type = "Course notes"
    elif any(keyword in filename_lower for keyword in ['a', 'assignment']):
        doc_type = "Assignment"
    elif 'tut' in filename_lower:
        doc_type = "Tutorial materials"
    elif 'test' in filename_lower:
        doc_type = "Test materials"
    
    # Identify key topics from content
    topics = _identify_topics(text_content)
    
    # Generate description
    if course_code:
        if doc_type == "Homework assignment":
            return f"{doc_type} for {course_code} {course_topic} course"
        elif doc_type == "Course notes":
            return f"{doc_type} for {course_code} {course_topic} course"
        elif doc_type == "Assignment":
            return f"{doc_type} for {course_code} {course_topic} course"
        else:
            return f"{doc_type} for {course_code} {course_topic} course"
    else:
        # Handle non-course documents
        if 'fyp' in filename_lower:
            return "Final Year Project report and research findings"
        elif 'mapf' in filename_lower:
            return "Research on Multi-Agent Pathfinding using genetic programming"
        elif 'network' in filename_lower:
            return "Network Science assignment covering network analysis"
        elif 'paxos' in filename_lower:
            return "Documentation on Paxos consensus algorithm"
        elif 'pca' in filename_lower:
            return "Notes on Principal Component Analysis and applications"
        elif 'vitae' in filename_lower:
            return "Personal curriculum vitae and academic background"
        elif topics:
            return f"Notes on {topics[0]} covering {', '.join(topics[1:3])}"
        else:
            return "Academic document covering mathematical concepts"


def _identify_topics(text_content: str) -> list:
    """Identify key mathematical topics from text content."""
    text_lower = text_content.lower()
    
    topic_keywords = {
        'algebra': ['algebra', 'ring', 'module', 'ideal', 'commutative', 'homological'],
        'analysis': ['analysis', 'calculus', 'differential', 'integral', 'measure', 'real analysis'],
        'topology': ['topology', 'topological', 'compact', 'continuous', 'metric'],
        'geometry': ['geometry', 'geometric', 'algebraic geometry', 'differential geometry'],
        'set_theory': ['set', 'function', 'relation', 'cardinal', 'ordinal'],
        'linear_algebra': ['linear', 'matrix', 'vector', 'eigenvalue', 'spectral'],
        'complex_analysis': ['complex', 'analytic', 'holomorphic', 'residue'],
        'number_theory': ['number', 'prime', 'divisor', 'congruence'],
        'graph_theory': ['graph', 'vertex', 'edge', 'cycle', 'path'],
        'algorithms': ['algorithm', 'search', 'pathfinding', 'optimization']
    }
    
    found_topics = []
    for topic_name, keywords in topic_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            found_topics.append(topic_name.replace('_', ' ').title())
    
    return found_topics[:3]  # Return top 3 topics


def _categorize_document_from_text(pdf_path: str, pdf_text: str, description: str) -> str:
    """Categorize a document based on its path, text content, and description."""
    filename = os.path.basename(pdf_path).lower()
    description_lower = description.lower()
    text_lower = pdf_text.lower()
    
    # Course code patterns
    course_codes = ['ma4261', 'ma4271', 'ma5204', 'ma5205', 'ma5209', 'ma5210', 'ma5211', 'ma5216', 'ma5232', 'ma5259', 'ma5271']
    
    if any(code in filename for code in course_codes):
        return "mathematics"
    elif any(keyword in filename for keyword in ['fyp', 'mapf', 'research']):
        return "research_papers"
    elif any(keyword in filename for keyword in ['network', 'algorithm', 'paxos', 'pca']):
        return "computer_science"
    elif 'vitae' in filename:
        return "personal"
    else:
        return "mathematics"  # Default to mathematics


def _categorize_document(pdf_path: str, description: str) -> str:
    """Categorize a document based on its path and description."""
    filename = os.path.basename(pdf_path).lower()
    description_lower = description.lower()
    
    # Course code patterns
    course_codes = ['ma4261', 'ma4271', 'ma5204', 'ma5205', 'ma5209', 'ma5210', 'ma5211', 'ma5216', 'ma5232', 'ma5259', 'ma5271']
    
    if any(code in filename for code in course_codes):
        return "mathematics"
    elif any(keyword in filename for keyword in ['fyp', 'mapf', 'research']):
        return "research_papers"
    elif any(keyword in filename for keyword in ['network', 'algorithm', 'paxos', 'pca']):
        return "computer_science"
    elif 'vitae' in filename:
        return "personal"
    else:
        return "mathematics"  # Default to mathematics


def _generate_collection_summary_from_categories(categories: dict, total_files: int) -> str:
    """Generate a summary of the document collection from categories."""
    summary_parts = [f"Collection contains {total_files} documents"]
    
    if categories:
        category_list = [f"{count} {cat.replace('_', ' ')}" for cat, count in categories.items()]
        summary_parts.append(f"Categories: {', '.join(category_list)}")
    
    return ". ".join(summary_parts)


def _generate_collection_summary(categories: dict, total_files: int, total_size: int) -> str:
    """Generate a summary of the document collection."""
    total_size_mb = round(total_size / (1024 * 1024), 1)
    
    summary_parts = [f"Collection contains {total_files} documents ({total_size_mb} MB)"]
    
    if categories:
        category_list = [f"{count} {cat.replace('_', ' ')}" for cat, count in categories.items()]
        summary_parts.append(f"Categories: {', '.join(category_list)}")
    
    return ". ".join(summary_parts)


def _generate_basic_description(pdf_path: str) -> str:
    """Generate basic description when PyMuPDF is not available."""
    filename = os.path.basename(pdf_path)
    filename_lower = filename.lower()
    
    # Basic course code detection
    course_codes = ['ma4261', 'ma4271', 'ma5204', 'ma5205', 'ma5209', 'ma5210', 'ma5211', 'ma5216', 'ma5232', 'ma5259', 'ma5271']
    
    for code in course_codes:
        if code in filename_lower:
            if 'hw' in filename_lower or 'homework' in filename_lower:
                return f"Homework for {code.upper()} course"
            elif 'notes' in filename_lower:
                return f"Notes for {code.upper()} course"
            else:
                return f"Materials for {code.upper()} course"
    
    # Handle other documents
    if 'fyp' in filename_lower:
        return "Final Year Project document"
    elif 'mapf' in filename_lower:
        return "Multi-Agent Pathfinding research"
    elif 'network' in filename_lower:
        return "Network Science assignment"
    else:
        return "Academic document"


# Example usage and testing
if __name__ == "__main__":
    # Test the function with text data
    test_path = "../docs/assets/public_doc/ma5204_notes.pdf"
    if os.path.exists(test_path):
        try:
            # Simulate text extraction
            import pymupdf
            doc = pymupdf.Document(test_path)
            text_content = ""
            if len(doc) > 0:
                text_content = doc[0].get_text()[:1000]  # First 1000 chars
            doc.close()
            
            test_data = [(test_path, text_content)]
            summary, descriptions = get_pdf_desc(test_data)
            print(f"Summary: {summary}")
            for path, desc in descriptions.items():
                print(f"Description: {desc}")
        except Exception as e:
            print(f"Error testing: {e}")
    else:
        print("Test file not found")
