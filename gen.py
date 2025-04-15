import pathlib

import jinja2


REPO_PATH = pathlib.Path(__file__).resolve().parent
SYMLINKS = [
    ("htaccess", ".htaccess"),
    ("style.css", "style.css"),
]


def gen_index() -> None:
    template_path = REPO_PATH / "index.html.j2"
    dest_path = REPO_PATH.parent / "index.html"

    env = jinja2.Environment(autoescape=True)
    template = env.from_string(template_path.read_text())

    dest_path.write_text(template.render())
    print("index.html generated.")


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
    gen_index()
