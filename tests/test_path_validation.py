from app.utils.path_validation import validate_file_path, validate_paths


def test_validate_file_path_rejects_traversal():
    assert validate_file_path("../etc/passwd") == "path_traversal"
    assert validate_file_path("foo/../bar") == "path_traversal"


def test_validate_file_path_rejects_long():
    assert validate_file_path("a" * 257) == "path_too_long"


def test_validate_file_path_rejects_invalid_chars():
    assert validate_file_path("file\x00.txt") == "invalid_characters"


def test_validate_file_path_accepts_valid():
    assert validate_file_path("data/file.csv") is None
    assert validate_file_path("utils/helper.py") is None


def test_validate_paths():
    assert validate_paths({"a.py": "base64"}) is None
    assert validate_paths({"../bad": "x"}) == "path_traversal"
