def test_register_and_get(tmp_path):
    from app import config  # pylint: disable=import-outside-toplevel
    from app.services.env_registry import get_env_image, register_environment  # pylint: disable=import-outside-toplevel

    config.settings.ENVIRONMENTS_DIR = str(tmp_path)
    register_environment("test-env", "my-image:tag", "python", "desc")
    assert get_env_image("test-env") == "my-image:tag"


def test_get_missing_env(tmp_path):
    from app import config  # pylint: disable=import-outside-toplevel
    from app.services.env_registry import get_env_image  # pylint: disable=import-outside-toplevel

    config.settings.ENVIRONMENTS_DIR = str(tmp_path)
    assert get_env_image("nonexistent") is None
