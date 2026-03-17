import re
from typing import Optional


def validate_file_path(path: str, max_len: int = 256) -> Optional[str]:
    if ".." in path:
        return "path_traversal"
    if len(path) > max_len:
        return "path_too_long"
    if not re.match(r"^[a-zA-Z0-9_.\-/]+$", path):
        return "invalid_characters"
    return None


def validate_paths(files: dict[str, str]) -> Optional[str]:
    for path in files:
        err = validate_file_path(path)
        if err:
            return err
    return None
