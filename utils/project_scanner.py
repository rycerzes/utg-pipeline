from pathlib import Path


def scan_cpp_files(project_dir):
    """
    Scan the given directory for .cc C++ source files.
    Returns a list of Path objects.
    """
    project_dir = Path(project_dir)
    return list(project_dir.glob("*.cc"))
