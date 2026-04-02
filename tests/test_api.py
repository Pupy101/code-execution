from unittest.mock import AsyncMock, MagicMock, patch


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_languages(client):
    r = client.get("/languages")
    assert r.status_code == 200
    data = r.json()
    assert "languages" in data
    assert len(data["languages"]) == 26
    ids = {x["id"] for x in data["languages"]}
    assert "javascript" in ids
    assert "nodejs" not in ids
    assert all("title" in x and "description" in x for x in data["languages"])


def test_execute_rejects_non_public_lang(client):
    r = client.post(
        "/api/v1/execute",
        json={"code": "1", "lang": "go_test"},
    )
    assert r.status_code == 422


@patch("app.api.execute.sandbox_client.run_code", new_callable=AsyncMock)
def test_execute_maps_markdown_javascript_to_nodejs(mock_run, client):
    mock_run.return_value = {"status": "Success", "run_result": {"stdout": "", "stderr": "", "return_code": 0}}
    r = client.post(
        "/api/v1/execute",
        json={"code": 'console.log("hi")', "lang": "javascript"},
    )
    assert r.status_code == 200
    mock_run.assert_awaited_once()
    assert mock_run.call_args.kwargs["language"] == "nodejs"


def test_execute_validation(client):
    r = client.post(
        "/api/v1/execute",
        json={"code": "print(1)", "lang": "python", "files": {"../bad": "x"}},
    )
    assert r.status_code == 400


@patch("app.api.execute.job_set")
@patch("app.api.execute.asyncio.create_task")
@patch("app.api.execute.sandbox_client.run_code", new_callable=AsyncMock)
def test_execute_async(mock_run, mock_create_task, mock_job_set, client):
    def _consume_task(coro):
        coro.close()
        return MagicMock()

    mock_create_task.side_effect = _consume_task
    mock_run.return_value = {"status": "Success", "run_result": {"stdout": "1\n", "stderr": "", "return_code": 0}}
    r = client.post(
        "/api/v1/execute/async",
        json={"code": "print(1)", "lang": "python"},
    )
    assert r.status_code == 200
    job_id = r.json()["id"]
    assert job_id
    mock_job_set.assert_called_once()
    assert mock_job_set.call_args[0][0] == job_id


@patch("app.api.execute._sandbox_sem")
def test_execute_async_overloaded(mock_sem, client):
    mock_sem.locked.return_value = True
    r = client.post(
        "/api/v1/execute/async",
        json={"code": "print(1)", "lang": "python"},
    )
    assert r.status_code == 503


@patch("app.api.execute.job_get")
def test_execute_async_status_not_found(mock_get, client):
    mock_get.return_value = None
    r = client.get("/api/v1/execute/async/nonexistent-id")
    assert r.status_code == 404


@patch("app.api.execute.job_get")
def test_execute_async_status_pending(mock_get, client):
    mock_get.return_value = {"status": "pending", "stdout": "", "stderr": "", "exit_code": 0}
    r = client.get("/api/v1/execute/async/some-id")
    assert r.status_code == 200
    assert r.json()["status"] == "pending"


@patch("app.api.execute.job_get")
def test_execute_async_status_finish(mock_get, client):
    mock_get.return_value = {"status": "finish", "stdout": "hello\n", "stderr": "", "exit_code": 0}
    r = client.get("/api/v1/execute/async/some-id")
    assert r.status_code == 200
    assert r.json()["status"] == "finish"
    assert r.json()["stdout"] == "hello\n"
