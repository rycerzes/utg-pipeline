from pathlib import Path

def list_functions_in_cpp_file(file_path):
    """
    Naive function to list function names in a C++ file (for coverage or analysis).
    Returns a list of function names (best effort, not a full parser).
    """
    import re
    file_path = Path(file_path)
    code = file_path.read_text()
    # Simple regex for function definitions (not perfect)
    pattern = re.compile(r'\b([\w:]+)\s+([\w:]+)\s*\([^)]*\)\s*\{')
    return [m.group(2) for m in pattern.finditer(code)]
