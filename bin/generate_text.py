#!/usr/bin/env python
import argparse
import shutil
import os
import re
import sys
from datetime import datetime

import pymupdf

get_ai_description = None

try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from vendor.ai_tools import get_ai_description
except ImportError as e:
    print(f"DEBUG: import ai_tools failed ({e})")
except Exception as e:
    print(f"DEBUG: import ai_tools failed ({e})")


class HtmlPath:
    def __init__(self, html_root_dir: str, htmlpath: str):
        assert htmlpath.startswith("/"), "htmlpath must be absolute"
        self.html_root_dir = html_root_dir
        self.htmlpath = htmlpath

    def to_path(self) -> str:
        return self.html_root_dir + self.htmlpath

    def __str__(self) -> str:
        return self.htmlpath

def copy_public_doc(input_dir: str, doc_htmldir: HtmlPath):
    output_dir = doc_htmldir.to_path()

    os.makedirs(output_dir, exist_ok=True)

    for name in os.listdir(input_dir):
        input_path = f"{input_dir}/{name}/main.pdf"
        output_path = f"{output_dir}/{name}.pdf"
        if os.path.exists(input_path):
            shutil.copyfile(input_path, output_path)

def get_pdf_dates(pdf_path: str) -> tuple[datetime, datetime]:
    def parse_pdf_date(date_str: str) -> datetime | None:
        if not date_str:
            return None
        if date_str.startswith("D:"):
            date_str = date_str[2:]  # Strip leading "D:" if present
        date_str = re.sub(r"[+-].*", "", date_str)  # Remove the timezone part like +08'00'
        dt = datetime.strptime(date_str[:14], "%Y%m%d%H%M%S")  # Parse the date
        return dt

    doc = pymupdf.Document(pdf_path)
    creation_date = parse_pdf_date(doc.metadata.get("creationDate"))
    modified_date = parse_pdf_date(doc.metadata.get("modDate"))
    if creation_date is None:
        creation_date = datetime.min
    if modified_date is None:
        modified_date = datetime.min

    return creation_date, modified_date


def datetime_to_str(dt: datetime) -> str:
    return dt.strftime("%d %b %Y")

def get_pdf_text(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text content from the PDF
    """
    try:
        doc = pymupdf.Document(pdf_path)
        text_content = ""
        
        # Extract text from first few pages for efficiency
        max_pages = min(3, len(doc))
        for page_num in range(max_pages):
            try:
                page_text = doc[page_num].get_text()
                text_content += page_text + " "
            except Exception:
                continue
        
        doc.close()
        
        # Clean up text: remove extra whitespace and normalize
        import re
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        return text_content
        
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return "" 

def generate_text_html(
        doc_htmldir: HtmlPath,
        text_template_path: str,
        text_output_path: str,
):
    doc_dir = doc_htmldir.to_path()
    html_template = open(text_template_path).read()

    item_list = []
    for name in sorted(os.listdir(doc_dir)):
        path = f"{doc_dir}/{name}"
        creation_date, modified_date = get_pdf_dates(path)
        item = (name, path, creation_date, modified_date)
        item_list.append(item)

    item_list.sort(key=lambda x: x[2], reverse=True)  # sort by modified date

    summary = ""
    description = {}
    
    if get_ai_description is not None:
        try:
            text_dict = {path: get_pdf_text(path) for name, path, creation_date, modified_date in item_list}
            summary, description = get_ai_description(text_dict)
            content = f"AI generated summary: {summary} <hr>\n"
        except Exception as e:
            print(f"DEBUG: get_ai_description failed ({e})")
            content = ""
    else:
        content = ""
    
    for name, path, creation_date, modified_date in item_list:
        modified_date_str = datetime_to_str(modified_date)

        comment = ""
        if path in description:
            comment = f'<small style="opacity: 0.6; color: #666; font-style: italic; filter: blur(0.3px);">(AI generated description: {description[path]})</small>'

        content += f"""
        <li>
            {modified_date_str}: <a href="{doc_htmldir}/{name}">{name}</a>
            {comment}
        </li>
        """

        print(f"DEBUG: generated entry for {name}")


    html = html_template.format(public_doc_content=content)
    with open(text_output_path, "w") as f:
        f.write(html)

    print(f"DEBUG: generated {len(item_list)} entries in {text_output_path}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html_root_dir", type=str)
    parser.add_argument("--doc_htmldir", type=str)
    parser.add_argument("--text_template_path", type=str)
    parser.add_argument("--text_output_path", type=str)
    parser.add_argument("--input_dir", type=str)
    args = parser.parse_args()


    DOC_HTMLDIR = HtmlPath(
        html_root_dir=args.html_root_dir,
        htmlpath=args.doc_htmldir,
    )

    copy_public_doc(
        input_dir=args.input_dir,
        doc_htmldir=DOC_HTMLDIR,
    )
    generate_text_html(
        doc_htmldir=DOC_HTMLDIR,
        text_template_path=args.text_template_path,
        text_output_path=args.text_output_path,
    )
