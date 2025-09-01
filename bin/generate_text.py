#!/usr/bin/env python
import sys;
import os;

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pydantic

import argparse
import os
from datetime import datetime

from src.util.pdf_util import get_pdf_dates, get_pdf_text
from src.util.util import HtmlPath
from src.util.pdf_util import get_pdf_text


def datetime_to_str(dt: datetime) -> str:
    return dt.strftime("%d %b %Y")


class DocInfo(pydantic.BaseModel):
    name: str
    category: str
    htmlpath: HtmlPath
    creation_date: datetime
    modified_date: datetime
    description: str


def get_pdfs_from_dir(doc_htmldir: HtmlPath) -> dict[str, list[DocInfo]]:
    """
    pdf path: <root_dir>/<category>/<project_name>/main.pdf
    """


    doc_info_dict: dict[str, list[DocInfo]] = {}
    for category in os.listdir(doc_htmldir.to_path()):
        category_dir = f"{doc_htmldir.to_path()}/{category}"
        if not os.path.isdir(category_dir):
            continue
        for name in os.listdir(category_dir):
            path = f"{category_dir}/{name}/main.pdf"
            htmlpath = HtmlPath(
                html_root_dir=doc_htmldir.html_root_dir,
                htmlpath=f"{doc_htmldir.htmlpath}/{category}/{name}/main.pdf",
            )
            if not os.path.exists(path):
                continue

            creation_date, modified_date = get_pdf_dates(path)

            description = get_pdf_text(path)
            description = " ".join(description.split()[:20])

            if category not in doc_info_dict:
                doc_info_dict[category] = []

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
    return f'<text style="opacity: 0.6; color: #666; font-style: italic; filter: blur(0.3px);"> {text}</text>'

def generate_text_html(
        doc_htmldir: HtmlPath,
        text_template_path: str,
        text_output_path: str,
):
    doc_info_dict: dict[str, list[DocInfo]] = get_pdfs_from_dir(doc_htmldir)

    content = ""
    for category, item_list in doc_info_dict.items():
        content += "<h2>" + category + "</h2>"

        item_list = sorted(item_list, key=lambda x: x.modified_date, reverse=True)

        for item in item_list:
            content += f"""
            <li>
                <a href="{item.htmlpath}">{item.name}</a> {blur_html_text(f"(last compiled {datetime_to_str(item.modified_date)})")}
                <br>
                {blur_html_text(f"({item.description})")}
            </li>
            """

    html_template = open(text_template_path).read()
    html = html_template.format(public_doc_content=content)
    with open(text_output_path, "w") as f:
        f.write(html)

    print(f"DEBUG: generated {sum(map(len, doc_info_dict.values()))} entries in {text_output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html_root_dir", type=str)
    parser.add_argument("--doc_htmldir", type=str)
    parser.add_argument("--text_template_path", type=str)
    parser.add_argument("--text_output_path", type=str)
    args = parser.parse_args()

    generate_text_html(
        doc_htmldir=HtmlPath(
            html_root_dir=args.html_root_dir,
            htmlpath=args.doc_htmldir,
        ),
        text_template_path=args.text_template_path,
        text_output_path=args.text_output_path,
    )
