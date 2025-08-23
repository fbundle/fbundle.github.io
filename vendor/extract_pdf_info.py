#!/usr/bin/env python3
import os
import json
import pymupdf
from pathlib import Path

def extract_pdf_info(pdf_path):
    """Extract information from a PDF file"""
    try:
        doc = pymupdf.Document(pdf_path)
        
        # Get metadata
        metadata = doc.metadata
        title = metadata.get('title', '')
        author = metadata.get('author', '')
        subject = metadata.get('subject', '')
        
        # Get first page text for content analysis
        first_page_text = ""
        if len(doc) > 0:
            first_page_text = doc[0].get_text()[:2000]  # First 2000 characters
        
        # Get page count
        page_count = len(doc)
        
        # Get file size
        file_size = os.path.getsize(pdf_path)
        
        return {
            "title": title,
            "author": author,
            "subject": subject,
            "first_page_text": first_page_text,
            "page_count": page_count,
            "file_size_kb": file_size // 1024
        }
    except Exception as e:
        return {
            "error": str(e),
            "file_size_kb": os.path.getsize(pdf_path) // 1024 if os.path.exists(pdf_path) else 0
        }

def analyze_content(text, filename):
    """Analyze the content to determine topic and description"""
    text_lower = text.lower()
    
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
    
    # Topic keywords
    topics = {
        'algebra': ['algebra', 'ring', 'module', 'ideal', 'commutative', 'homological'],
        'analysis': ['analysis', 'calculus', 'differential', 'integral', 'measure', 'real analysis'],
        'topology': ['topology', 'topological', 'compact', 'continuous', 'metric'],
        'geometry': ['geometry', 'geometric', 'algebraic geometry', 'differential geometry'],
        'set_theory': ['set', 'function', 'relation', 'cardinal', 'ordinal'],
        'linear_algebra': ['linear', 'matrix', 'vector', 'eigenvalue', 'spectral'],
        'complex_analysis': ['complex', 'analytic', 'holomorphic', 'residue'],
        'number_theory': ['number', 'prime', 'divisor', 'congruence'],
        'graph_theory': ['graph', 'vertex', 'edge', 'cycle', 'path'],
        'algorithms': ['algorithm', 'search', 'pathfinding', 'optimization'],
        'computer_science': ['network', 'distributed', 'consensus', 'paxos'],
        'research': ['research', 'project', 'thesis', 'paper']
    }
    
    # Determine course code
    course_code = None
    course_topic = None
    for code, topic in course_patterns.items():
        if code in filename.lower():
            course_code = code.upper()
            course_topic = topic
            break
    
    # Determine main topic
    main_topic = "General Mathematics"
    max_matches = 0
    for topic_name, keywords in topics.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        if matches > max_matches:
            max_matches = matches
            main_topic = topic_name.replace('_', ' ').title()
    
    # Generate description
    if course_code:
        if 'homework' in filename.lower() or 'hw' in filename.lower():
            description = f"Homework assignment for {course_code} {course_topic} course"
        elif 'notes' in filename.lower():
            description = f"Course notes for {course_code} {course_topic} course"
        elif 'assignment' in filename.lower() or 'a' in filename.lower():
            description = f"Assignment for {course_code} {course_topic} course"
        else:
            description = f"Course materials for {course_code} {course_topic} course"
    else:
        # Analyze filename for other documents
        if 'fyp' in filename.lower():
            description = "Final Year Project report and research findings"
        elif 'mapf' in filename.lower():
            description = "Multi-Agent Pathfinding research using genetic programming"
        elif 'network' in filename.lower():
            description = "Network Science assignment covering network analysis"
        elif 'paxos' in filename.lower():
            description = "Documentation on Paxos consensus algorithm for distributed systems"
        elif 'pca' in filename.lower():
            description = "Principal Component Analysis notes and applications"
        elif 'vitae' in filename.lower():
            description = "Personal curriculum vitae and academic background"
        else:
            description = f"Document covering {main_topic.lower()} concepts and applications"
    
    return {
        "topic": main_topic,
        "description": description,
        "course_code": course_code
    }

def main():
    # Path to the public_doc directory
    public_doc_dir = Path("../docs/assets/public_doc")
    
    if not public_doc_dir.exists():
        print(f"Directory {public_doc_dir} does not exist!")
        return
    
    documents = {}
    total_size = 0
    
    # Process each PDF file
    for pdf_file in sorted(public_doc_dir.glob("*.pdf")):
        filename = pdf_file.name
        print(f"Processing {filename}...")
        
        # Extract PDF information
        pdf_info = extract_pdf_info(pdf_file)
        
        # Analyze content
        content_analysis = analyze_content(pdf_info.get('first_page_text', ''), filename)
        
        # Determine category
        if pdf_info.get('course_code'):
            category = "mathematics"
        elif any(keyword in filename.lower() for keyword in ['fyp', 'mapf', 'research']):
            category = "research_papers"
        elif any(keyword in filename.lower() for keyword in ['network', 'algorithm', 'paxos', 'pca']):
            category = "computer_science"
        elif 'vitae' in filename.lower():
            category = "personal"
        else:
            category = "mathematics"  # Default to mathematics
        
        # Create document entry
        documents[filename] = {
            "category": category,
            "topic": content_analysis["topic"],
            "description": content_analysis["description"],
            "size_kb": pdf_info["file_size_kb"],
            "pages": pdf_info.get("page_count", "Unknown"),
            "course_code": content_analysis.get("course_code"),
            "author": pdf_info.get("author", ""),
            "title": pdf_info.get("title", "")
        }
        
        total_size += pdf_info["file_size_kb"]
    
    # Count categories
    categories = {}
    for doc in documents.values():
        cat = doc["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    # Create summary
    summary = {
        "total_documents": len(documents),
        "categories": categories,
        "total_size_mb": round(total_size / 1024, 1),
        "date_range": "Academic documents spanning multiple years",
        "description": "A comprehensive collection of academic materials including mathematics coursework, computer science assignments, research papers, and personal documents. The collection covers advanced topics in algebra, analysis, geometry, algorithms, and network science."
    }
    
    # Create final structure
    result = {
        "summary": summary,
        "documents": documents
    }
    
    # Save to JSON file
    output_file = "public_doc_description_updated.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nUpdated description saved to {output_file}")
    print(f"Total documents processed: {len(documents)}")
    print(f"Total size: {total_size/1024:.1f} MB")
    print(f"Categories: {categories}")

if __name__ == "__main__":
    main()
