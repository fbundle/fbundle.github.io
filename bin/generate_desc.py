import argparse


class HtmlPath:
    def __init__(self, html_root_dir: str, htmlpath: str):
        assert htmlpath.startswith("/"), "htmlpath must be absolute"
        self.html_root_dir = html_root_dir
        self.htmlpath = htmlpath

    def to_path(self) -> str:
        return self.html_root_dir + self.htmlpath

    def __str__(self) -> str:
        return self.htmlpath

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