import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("SANDBOX_FUSION_URL", "http://localhost:8080")
os.environ.setdefault("ENVIRONMENTS_DIR", "config/environments")


@pytest.fixture
def client():
    from app.main import app  # pylint: disable=import-outside-toplevel

    return TestClient(app)
