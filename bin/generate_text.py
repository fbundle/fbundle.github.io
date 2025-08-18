#!/usr/bin/env python
import os
import shutil
import re
from datetime import datetime
import pymupdf

doc_dir = "docs/generate/public_doc"
html_doc_dir = "/generate/public_doc"
html_target = (
    "docs/posts/text.template.html",
    "docs/posts/text.html",
)

src_dir = "/Users/khanh/mathdoc/public_doc"

def copy_doc():
    os.makedirs(doc_dir, exist_ok=True)

    for name in os.listdir(src_dir):
        src_path = f"{src_dir}/{name}/main.pdf"
        if not os.path.exists(src_path):
            continue
        dst_path = f"{doc_dir}/{name}.pdf"

        shutil.copyfile(src_path, dst_path)


def get_pdf_dates(pdf_path: str) -> tuple[datetime, datetime]:
    def parse_pdf_date(date_str: str) -> datetime | None:
        if not date_str:
            return None
        if date_str.startswith("D:"):
            date_str = date_str[2:] # Strip leading "D:" if present
        date_str = re.sub(r"[+-].*", "", date_str) # Remove the timezone part like +08'00'
        dt = datetime.strptime(date_str[:14], "%Y%m%d%H%M%S") # Parse the date
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

def gen_html():
    html_template = open(html_target[0]).read()

    item_list = []
    for name in sorted(os.listdir(doc_dir)):
        creation_date, modified_date = get_pdf_dates(f"{doc_dir}/{name}")
        item = (name, creation_date, modified_date)
        item_list.append(item)

    item_list.sort(key=lambda x: x[2], reverse=True) # sort by modified date

    content = ""
    for name, creation_date, modified_date in item_list:
        modified_date_str = datetime_to_str(modified_date)
        link = f"{html_doc_dir}/{name}"
        content += f'<li> {modified_date_str}: <a href="{link}">{name}</a> </li>' + '\n'

    html = html_template.format(public_doc_content=content)
    with open(html_target[1], "w") as f:
        f.write(html)

if __name__ == "__main__":
    copy_doc()
    gen_html()
    

    
