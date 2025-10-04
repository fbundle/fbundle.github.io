#!/usr/bin/env python
"""
HTML Page Generator for Personal Website

This script processes HTML page templates and generates complete HTML pages
by inserting page content into a master template. It recursively searches
for .html files in the input directory and wraps their content with the
provided template.

Usage:
    python generate_pages.py --input_dir src/pages --output_dir docs/pages --template src/template.html

Author: Khanh
Repository: fbundle.github.io
"""
import sys; import os; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import os
import pathlib


def generate_pages(input_dir: str, output_dir: str, template_path: str) -> None:
    """
    Generate HTML pages by inserting content into a master template.
    
    This function:
    1. Reads the master template file
    2. Recursively finds all .html files in the input directory
    3. For each file, wraps its content with template markers
    4. Inserts the wrapped content into the master template
    5. Writes the final HTML to the output directory
    
    Args:
        input_dir (str): Directory containing source HTML files to process
        output_dir (str): Directory where generated HTML files will be saved
        template_path (str): Path to the master HTML template file
    """
    # Read the master template that will wrap all page content
    template: str = open(template_path).read()

    total_pages = 0
    
    # Recursively find all .html files in the input directory
    for path in pathlib.Path(input_dir).rglob("*.html"):
        # Get relative path to preserve directory structure in output
        rel_path = path.relative_to(input_dir)

        # Read the page content and wrap it with template markers
        # These markers help identify where content should be inserted
        content = "\n<!-- INSERT_CONTENT_BEGIN -->\n" + open(path).read() + "\n<!-- INSERT_CONTENT_END -->\n"

        # Insert the wrapped content into the master template
        # The template should have a {content} placeholder for this insertion
        html = template.format(content=content)

        # Create the output file path, preserving directory structure
        output_path = os.path.join(output_dir, rel_path)
        # Ensure the output directory exists (create if needed)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Write the generated HTML to the output file
        open(output_path, "w").write(html)

        print(f"DEBUG: generated {output_path}")
        total_pages += 1

    print(f"DEBUG: generated {total_pages} pages")



if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Generate HTML pages from templates and content files"
    )
    parser.add_argument(
        "--input_dir", 
        type=str, 
        required=True,
        help="Directory containing source HTML files to process"
    )
    parser.add_argument(
        "--output_dir", 
        type=str, 
        required=True,
        help="Directory where generated HTML files will be saved"
    )
    parser.add_argument(
        "--template", 
        type=str, 
        required=True,
        help="Path to the master HTML template file"
    )
    args = parser.parse_args()

    # Generate pages using the provided arguments
    generate_pages(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        template_path=args.template,
    )



