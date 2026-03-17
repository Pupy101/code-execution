# API Reference

## Health

```
GET /health
```

Response: `200 OK`, body: `{"status": "ok"}`

## Execute (Sync)

```
POST /api/v1/execute
Content-Type: application/json

{
  "code": "print(1+1)",
  "lang": "python",
  "timeout": 30,
  "memory": 256,
  "cpu": 1.0,
  "network": false,
  "env": null,
  "files": {}
}
```

Response:
```json
{
  "status": "success",
  "stdout": "2\n",
  "stderr": "",
  "exit_code": 0
}
```

Status: `success` | `timeout` | `error` | `memory_limit`

При переполнении очереди: `503`, body: `{"error": "queue_full", "message": "...", "details": {...}}`

## Execute (Async)

```
POST /api/v1/execute/async
Body: (то же что sync)
Response: {"id": "uuid"}

GET /api/v1/execute/async/{id}
Response: {
  "status": "pending" | "timeout" | "finish",
  "stdout": "...",
  "stderr": "...",
  "exit_code": 0
}
```

## Environments

```
POST /api/v1/environments
Body: {"id": "ml-python", "image": "my-registry/ml-env:v1", "lang": "python", "desc": "..."}
Response: {"id": "ml-python", "image": "...", "status": "registered"}

GET /api/v1/environments
Response: {"environments": [{...}]}

PUT /api/v1/environments/{id}
Body: {"image": "...", "desc": "..."}

DELETE /api/v1/environments/{id}
```

## Sessions (Python)

```
POST /api/v1/sessions
Body: {"ttl": 1800, "env": null, "memory": 512, "cpu": 1.0}
Response: {"id": "uuid"}

POST /api/v1/sessions/{id}/execute
Body: {"code": "x = 1"}
Response: {"status": "success", "stdout": "", "stderr": ""}

POST /api/v1/sessions/{id}/files
Body: {"files": {"data.csv": "base64...", "utils/helper.py": "base64..."}}
Response: {"uploaded": ["data.csv", "utils/helper.py"]}

GET /api/v1/sessions/{id}/files
Response: {"files": ["data.csv", "utils/helper.py"]}

POST /api/v1/sessions/{id}/finish
Response: {"status": "finished"}
```

## Формат ошибок

```json
{
  "error": "queue_full",
  "message": "Очередь переполнена",
  "details": {"queue_len": 500, "max": 500}
}
```

Коды: `queue_full`, `queue_timeout`, `task_timeout`, `invalid_env`, `path_traversal`, `validation_error`
