import pytest
from unittest.mock import patch


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_execute_validation(client):
    r = client.post(
        "/api/v1/execute",
        json={"code": "print(1)", "lang": "python", "files": {"../bad": "x"}},
    )
    assert r.status_code == 400


@patch("app.api.execute.get_queue_len")
@patch("app.api.execute.enqueue")
def test_execute_async(mock_enqueue, mock_len, client):
    mock_len.return_value = 0
    mock_enqueue.return_value = "job-123"
    r = client.post(
        "/api/v1/execute/async",
        json={"code": "print(1)", "lang": "python"},
    )
    assert r.status_code == 200
    assert r.json()["id"] == "job-123"


@patch("app.api.execute.get_queue_len")
def test_execute_async_queue_full(mock_len, client):
    mock_len.return_value = 500
    r = client.post(
        "/api/v1/execute/async",
        json={"code": "print(1)", "lang": "python"},
    )
    assert r.status_code == 503
