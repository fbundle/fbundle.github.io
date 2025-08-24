#!/usr/bin/env python
from src.util.util import HtmlPath

import argparse


def generate_public_doc_desc(doc_htmldir: HtmlPath, desc_output_path: str):





    raise NotImplemented

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html_root_dir", type=str)
    parser.add_argument("--doc_htmldir", type=str)
    parser.add_argument("--desc_output_path", type=str)
    args = parser.parse_args()


    DOC_HTMLDIR = HtmlPath(
        html_root_dir=args.html_root_dir,
        htmlpath=args.doc_htmldir,
    )

    generate_public_doc_desc(
        doc_htmldir=DOC_HTMLDIR,
        desc_output_path=args.desc_output_path,
    )