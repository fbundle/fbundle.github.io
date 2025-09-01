import pydantic
from pydantic import field_validator


class HtmlPath(pydantic.BaseModel):
    html_root_dir: str
    htmlpath: str
    @field_validator("htmlpath")
    def htmlpath_must_start_with_slash(cls, v):
        assert v.startswith("/"), "htmlpath must be absolute"
        return v

    def to_path(self) -> str:
        return self.html_root_dir + self.htmlpath

    def __str__(self) -> str:
        return self.htmlpath

def get_htmlpath_from_path(path: str, html_root_dir: str) -> HtmlPath:
    path = os.path.relpath(
        path=os.path.abspath(path),
        start=os.path.abspath(html_root_dir),
    )
    return HtmlPath(html_root_dir=html_root_dir, htmlpath=path)
