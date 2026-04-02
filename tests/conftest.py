import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("SANDBOX_FUSION_URL", "http://localhost:8080")

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
