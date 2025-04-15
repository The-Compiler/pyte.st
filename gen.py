from typing import Iterator
import dataclasses
import pathlib
import urllib.parse

import jinja2
import requests
import bs4


REPO_PATH = pathlib.Path(__file__).resolve().parent
SYMLINKS = [
    ("htaccess", ".htaccess"),
    ("style.css", "style.css"),
    ("style-vars.css", "style-vars.css"),
]


@dataclasses.dataclass
class Page:
    name: str
    dest: str
    title: str = ""


def gen_index(pages: list[Page]) -> None:
    template_path = REPO_PATH / "index.html.j2"
    dest_path = REPO_PATH.parent / "index.html"

    env = jinja2.Environment(autoescape=True)
    template = env.from_string(template_path.read_text())

    dest_path.write_text(template.render(pages=pages))
    print("index.html generated.")


def parse_htaccess() -> Iterator[Page]:
    htaccess_path = REPO_PATH / "htaccess"
    for line in htaccess_path.read_text().splitlines():
        try:
            cmd, src, dest = line.split()
        except ValueError:
            print(line)
            raise

        assert cmd == "Redirect", line
        yield Page(src.removeprefix("/"), dest)


def fill_title(page: Page) -> None:
    fragment = urllib.parse.urlparse(page.dest).fragment

    r = requests.get(page.dest)
    r.raise_for_status()

    soup = bs4.BeautifulSoup(r.text, "html.parser")

    assert soup.title is not None, page
    assert soup.title.string is not None, page
    page.title = soup.title.string.removesuffix(" - pytest documentation")

    if fragment:
        fragment_elem = soup.find(id=fragment)
        assert fragment_elem is not None, page

        # For pytest docs
        if fragment_elem.name == "span":
            section = fragment_elem.find_parent("section")
            assert section is not None, page
            fragment_elem = section.find("h2")
            assert fragment_elem is not None, page

        assert fragment_elem.text, page
        title = fragment_elem.text.rstrip("¶")
        page.title += f": {title}"

    print(page.title)


def create_symlinks() -> None:
    for repo_name, dest_name in SYMLINKS:
        repo_path = REPO_PATH / repo_name
        dest_path = REPO_PATH.parent / dest_name
        try:
            dest_path.symlink_to(repo_path)
        except FileExistsError:
            print(f"{dest_path} already exists, skipping.")


if __name__ == "__main__":
    create_symlinks()
    pages = list(parse_htaccess())
    print()
    for page in pages:
        fill_title(page)
    print()
    gen_index(pages)
