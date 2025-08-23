import argparse
import os
import shutil


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html_root_dir", type=str)
    parser.add_argument("--doc_htmldir", type=str)
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
