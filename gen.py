import re
from typing import Iterator
import dataclasses
import pathlib
import urllib.parse
import time

import jinja2
import requests
import bs4


REPO_PATH = pathlib.Path(__file__).resolve().parent
SYMLINKS = [
    ("htaccess", ".htaccess"),
    ("style.css", "style.css"),
    ("style-vars.css", "style-vars.css"),
]
TITLE_SUFFIX_RE = r" ([-— ] .* documentation|\| mathspp)"


@dataclasses.dataclass
class Page:
    name: str
    dest: str
    title: str = ""

    def _parsed(self) -> urllib.parse.ParseResult:
        return urllib.parse.urlparse(self.dest)

    @property
    def is_pytest_doc(self) -> bool:
        return self._parsed().hostname == "docs.pytest.org"

    @property
    def fragment(self) -> str:
        return self._parsed().fragment

    @property
    def hostname(self) -> str:
        hostname = self._parsed().hostname
        assert hostname is not None
        return hostname


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
    r = requests.get(page.dest)
    r.raise_for_status()

    soup = bs4.BeautifulSoup(r.text, "html.parser")

    assert soup.title is not None, page
    assert soup.title.string is not None, page
    page.title = re.sub(TITLE_SUFFIX_RE, "", soup.title.string)

    print(page.title)
    time.sleep(0.5)


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
    pages = sorted(parse_htaccess(), key=lambda p: p.name)
    print()
    for page in pages:
        fill_title(page)
    print()
    gen_index(pages)
