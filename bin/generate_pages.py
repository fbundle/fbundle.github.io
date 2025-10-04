#!/usr/bin/env python
import sys; import os; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import argparse
import os
import pathlib


def generate_pages(input_dir: str,output_dir: str, template_path: str):
    template: str = open(template_path).read()

    total_pages = 0
    for path in pathlib.Path(input_dir).rglob("*.html"):
        rel_path = path.relative_to(input_dir)

        content = "\n<!-- INSERT_CONTENT_BEGIN -->\n" + open(path).read() + "\n<!-- INSERT_CONTENT_END -->\n"

        html = template.format(content=content)

        output_path = os.path.join(output_dir, rel_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        open(output_path, "w").write(html)

        print(f"DEBUG: generated {output_path}")
        total_pages += 1

    print(f"DEBUG: generated {total_pages} pages")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str)
    parser.add_argument("--output_dir", type=str)
    parser.add_argument("--template", type=str)
    args = parser.parse_args()

    generate_pages(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        template_path=args.template,
    )



