import pathlib

REPO_PATH = pathlib.Path(__file__).resolve().parent
SYMLINKS = [
    ("htaccess", ".htaccess"),
    ("style.css", "style.css"),
]


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
