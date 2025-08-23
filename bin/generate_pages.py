import argparse
import os
import pathlib


def generate_pages(input_dir: str,output_dir: str):
    template: str = open(os.path.join(input_dir, "template.html")).read()

    content_dir = os.path.join(input_dir, "content")
    for path in pathlib.Path(content_dir).rglob("*.html"):
        rel_path = path.relative_to(content_dir)

        content = "\n<!-- INSERT_CONTENT_BEGIN -->\n" + open(path).read() + "\n<!-- INSERT_CONTENT_END -->\n"

        html = template.format(content=content)

        output_path = os.path.join(output_dir, rel_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        open(output_path, "w").write(html)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str)
    parser.add_argument("--output_dir", type=str)
    args = parser.parse_args()

    generate_pages(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
    )



