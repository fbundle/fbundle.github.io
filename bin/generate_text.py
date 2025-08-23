#!/usr/bin/env python
import argparse
import shutil
import os
import re
from datetime import datetime
import pymupdf

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





def generate_text_html(
        doc_htmldir: HtmlPath,
        text_template_path: str,
        text_output_path: str,
):
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
    doc_dir = doc_htmldir.to_path()

    html_template = open(text_template_path).read()

    item_list = []
    for name in sorted(os.listdir(doc_dir)):
        creation_date, modified_date = get_pdf_dates(f"{doc_dir}/{name}")
        item = (name, creation_date, modified_date)
        item_list.append(item)

    item_list.sort(key=lambda x: x[2], reverse=True)  # sort by modified date

    content = ""
    for name, creation_date, modified_date in item_list:
        modified_date_str = datetime_to_str(modified_date)

        content += f"""
        <li>
            {modified_date_str}: <a href="{doc_htmldir}/{name}">{name}</a>
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
