import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def list_project_files():
    """Return all project files while ignoring venv and cache files."""

    files = []

    for root, directories, filenames in os.walk(PROJECT_ROOT):

        # Ignore unnecessary folders
        directories[:] = [
            d for d in directories
            if d not in {"venv", "__pycache__", ".git"}
        ]

        for filename in filenames:
            full_path = os.path.join(root, filename)

            relative_path = Path(full_path).relative_to(PROJECT_ROOT).as_posix()

            files.append(relative_path)

    return files


def create_project_file(relative_path, content):
    """Create a new file inside the project safely."""

    full_path = (PROJECT_ROOT / relative_path).resolve()
    if not full_path.is_relative_to(PROJECT_ROOT):
        raise ValueError("Access denied.")

    # Don't overwrite existing files
    if full_path.exists():
        raise FileExistsError(
            f"File already exists: {relative_path}"
        )

    # Create parent folders if needed
    full_path.parent.mkdir(parents=True, exist_ok=True)

    # Create file
    with open(
        str(full_path),
        "w",
        encoding="utf-8"
    ) as file:
        file.write(content)

    return f"Created: {relative_path}"


def read_project_file(relative_path):
    """Read a file from the project safely."""

    full_path = (PROJECT_ROOT / relative_path).resolve()
    if not full_path.is_relative_to(PROJECT_ROOT):
        raise ValueError("Access denied.")

    if not full_path.is_file():
        raise FileNotFoundError(
            f"File not found: {relative_path}"
        )

    with open(
        str(full_path),
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


if __name__ == "__main__":

    print("\nPROJECT FILES:\n")

    for file in list_project_files():
        print(file)

