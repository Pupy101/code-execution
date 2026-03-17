import re


def validate_file_path(path: str, max_len: int = 256) -> str | None:
    if ".." in path:
        return "path_traversal"
    if len(path) > max_len:
        return "path_too_long"
    if not re.match(r"^[a-zA-Z0-9_.\-/]+$", path):
        return "invalid_characters"
    return None


def validate_paths(files: dict[str, str]) -> str | None:
    for path in files:
        err = validate_file_path(path)
        if err:
            return err
    return None
