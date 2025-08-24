#!/usr/bin/env python
import os
import sys
from typing import Optional

import pydantic

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import os
from datetime import datetime

from src.util.pdf_util import get_pdf_dates, get_pdf_text
from src.util.util import HtmlPath


def datetime_to_str(dt: datetime) -> str:
    return dt.strftime("%d %b %Y")


class DocDescription(pydantic.BaseModel):
    summary: str
    description: dict[str, str]


def generate_text_html(
        doc_htmldir: HtmlPath,
        text_template_path: str,
        text_output_path: str,
        desc_input_path: str = "",
):
    doc_dir = doc_htmldir.to_path()
    html_template = open(text_template_path).read()

    item_list = []
    for name in sorted(os.listdir(doc_dir)):
        path = f"{doc_dir}/{name}"
        creation_date, modified_date = get_pdf_dates(path)
        text_content = get_pdf_text(path).strip()
        item = (name, text_content, creation_date, modified_date)
        item_list.append(item)

    item_list.sort(key=lambda x: x[2], reverse=True)  # sort by modified date

    desc = DocDescription(
        summary="",
        description={},
    )

    if len(desc_input_path) > 0 and os.path.exists(desc_input_path):
        try:
            desc = pydantic.BaseModel.model_validate_json(open(desc_input_path).read())
        except Exception as e:
            print(f"DEBUG: failed to load {desc_input_path}: {e}")
        finally:
            desc = DocDescription(
                summary="",
                description={},
            )

    content = ""
    if len(desc.summary) > 0:
        content += f"AI summary: {desc.summary}<hr>"
    for name, text_content, creation_date, modified_date in item_list:
        modified_date_str = datetime_to_str(modified_date)

        comment = ""
        description = desc.description.get(name, "")
        if len(description) > 0:
            comment = f'<small style="opacity: 0.6; color: #666; font-style: italic; filter: blur(0.3px);">(AI generated description: {description})</small>'

        content += f"""
        <li>
            {modified_date_str}: <a href="{doc_htmldir}/{name}">{name}</a>
            <br>
            {comment}
        </li>
        """

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
    parser.add_argument("--desc_input_path", type=str, default="")
    args = parser.parse_args()

    DOC_HTMLDIR = HtmlPath(
        html_root_dir=args.html_root_dir,
        htmlpath=args.doc_htmldir,
    )

    generate_text_html(
        doc_htmldir=DOC_HTMLDIR,
        desc_input_path=args.desc_input_path,
        text_template_path=args.text_template_path,
        text_output_path=args.text_output_path,
    )
