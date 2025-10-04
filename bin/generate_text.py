#!/usr/bin/env python
"""
Academic Document Text Generator for Personal Website

This script scans academic documents (PDFs) and generates HTML content for a
text/posts page. It extracts metadata from PDF files including creation/modification
dates and text content, then organizes them by category and generates formatted
HTML for display on the website.

The script expects PDF files to be organized in the following structure:
    <root_dir>/<category>/<project_name>/main.pdf

Usage:
    python generate_text.py --html_root_dir docs --doc_htmldir /assets/public_doc \
        --text_template_path docs/pages/posts/text.template.html \
        --text_output_path docs/pages/posts/text.html

Author: Khanh
Repository: fbundle.github.io
"""

import sys; import os; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pydantic
import argparse
import os
from datetime import datetime

from src.util.pdf_util import get_pdf_dates, get_pdf_text
from src.util.util import HtmlPath


def datetime_to_str(dt: datetime) -> str:
    """
    Convert a datetime object to a human-readable string format.
    
    Args:
        dt (datetime): The datetime object to format
        
    Returns:
        str: Formatted date string (e.g., "15 Jan 2023")
    """
    return dt.strftime("%d %b %Y")


class DocInfo(pydantic.BaseModel):
    """
    Data model for academic document information.
    
    This class represents metadata about an academic document including
    its name, category, web path, dates, and description.
    """
    name: str                    # Name of the document/project
    category: str                # Category/folder name (e.g., "study_notes", "original_works")
    htmlpath: HtmlPath           # Web path for accessing the document
    creation_date: datetime      # When the document was created
    modified_date: datetime      # When the document was last modified
    description: str             # Brief description extracted from document content


def get_pdfs_from_dir(doc_htmldir: HtmlPath) -> dict[str, list[DocInfo]]:
    """
    Scan directory structure and extract information from PDF documents.
    
    Expected directory structure:
        <root_dir>/<category>/<project_name>/main.pdf
    
    For example:
        docs/assets/public_doc/study_notes/calculus/main.pdf
    
    Args:
        doc_htmldir (HtmlPath): Path object representing the documents directory
        
    Returns:
        dict[str, list[DocInfo]]: Dictionary mapping category names to lists of DocInfo objects
    """
    doc_info_dict: dict[str, list[DocInfo]] = {}
    
    # Iterate through each category directory
    for category in os.listdir(doc_htmldir.to_path()):
        category_dir = f"{doc_htmldir.to_path()}/{category}"
        if not os.path.isdir(category_dir):
            continue
            
        # Iterate through each project in the category
        for name in os.listdir(category_dir):
            # Construct path to main.pdf file
            path = f"{category_dir}/{name}/main.pdf"
            # Create HTML path for web access
            htmlpath = HtmlPath(
                html_root_dir=doc_htmldir.html_root_dir,
                htmlpath=f"{doc_htmldir.htmlpath}/{category}/{name}/main.pdf",
            )
            
            # Skip if main.pdf doesn't exist
            if not os.path.exists(path):
                continue

            # Extract creation and modification dates from PDF
            creation_date, modified_date = get_pdf_dates(path)

            # Extract text content and create a brief description
            description = get_pdf_text(path)
            # Take first 20 words and add ellipsis for brevity
            description = " ".join(description.split()[:20]) + " ..."

            # Initialize category list if it doesn't exist
            if category not in doc_info_dict:
                doc_info_dict[category] = []

            # Add document information to the category
            doc_info_dict[category].append(DocInfo(
                name=name,
                category=category,
                htmlpath=htmlpath,
                creation_date=creation_date,
                modified_date=modified_date,
                description=description,
            ))
            
    return doc_info_dict


def blur_html_text(text: str) -> str:
    """
    Apply visual blur effect to text using CSS styling.
    
    This function wraps text with HTML styling to make it appear
    slightly blurred and muted, typically used for metadata or
    less important information.
    
    Args:
        text (str): The text to blur
        
    Returns:
        str: HTML-wrapped text with blur styling
    """
    return f'<text style="opacity: 0.6; color: #666; font-style: italic; filter: blur(0.3px);"> {text}</text>'


def generate_text_html(
        doc_htmldir: HtmlPath,
        text_template_path: str,
        text_output_path: str,
) -> None:
    """
    Generate HTML content for the text/posts page from academic documents.
    
    This function:
    1. Scans the documents directory for PDF files
    2. Extracts metadata and content from each PDF
    3. Organizes documents by category
    4. Generates HTML content with links and descriptions
    5. Inserts the content into a template and saves the final HTML
    
    Args:
        doc_htmldir (HtmlPath): Path to the documents directory
        text_template_path (str): Path to the HTML template file
        text_output_path (str): Path where the final HTML will be saved
    """
    # Get document information organized by category
    doc_info_dict: dict[str, list[DocInfo]] = get_pdfs_from_dir(doc_htmldir)

    content = ""
    
    # Generate HTML content for each category
    for category, item_list in doc_info_dict.items():
        # Add category header
        content += "<h2>" + category + "</h2>"

        # Sort items by modification date (newest first)
        item_list = sorted(item_list, key=lambda x: x.modified_date, reverse=True)

        # Generate HTML for each document in the category
        for item in item_list:
            content += f"""
            <li>
                <a href="{item.htmlpath}">{item.name}</a> {blur_html_text(f"(last compiled {datetime_to_str(item.modified_date)})")}
                <br>
                {blur_html_text(f"({item.description})")}
            </li>
            """

    # Read the HTML template and insert the generated content
    html_template = open(text_template_path).read()
    html = html_template.format(public_doc_content=content)
    
    # Write the final HTML to the output file
    with open(text_output_path, "w") as f:
        f.write(html)

    # Print summary of generated content
    total_entries = sum(map(len, doc_info_dict.values()))
    print(f"DEBUG: generated {total_entries} entries in {text_output_path}")


if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Generate HTML text posts from academic PDF documents"
    )
    parser.add_argument(
        "--html_root_dir", 
        type=str, 
        required=True,
        help="Root directory for HTML output (e.g., 'docs')"
    )
    parser.add_argument(
        "--doc_htmldir", 
        type=str, 
        required=True,
        help="HTML path to documents directory (e.g., '/assets/public_doc')"
    )
    parser.add_argument(
        "--text_template_path", 
        type=str, 
        required=True,
        help="Path to the HTML template for text posts"
    )
    parser.add_argument(
        "--text_output_path", 
        type=str, 
        required=True,
        help="Path where the generated text HTML will be saved"
    )
    args = parser.parse_args()

    # Generate text HTML using the provided arguments
    generate_text_html(
        doc_htmldir=HtmlPath(
            html_root_dir=args.html_root_dir,
            htmlpath=args.doc_htmldir,
        ),
        text_template_path=args.text_template_path,
        text_output_path=args.text_output_path,
    )
