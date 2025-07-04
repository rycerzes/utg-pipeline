from pathlib import Path


def read_file(file_path):
    """Read the contents of a file and return as string."""
    file_path = Path(file_path)
    with open(file_path, "r") as f:
        return f.read()


def write_file(file_path, content):
    """Write the given content to a file."""
    file_path = Path(file_path)
    with open(file_path, "w") as f:
        f.write(content)
