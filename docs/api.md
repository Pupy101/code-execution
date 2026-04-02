# API Reference

## Health

```
GET /health
```

```json
{"status": "ok"}
```

---

## Languages

```
GET /languages
```

Возвращает список поддерживаемых языков. Значение поля `id` используется как `lang` в запросах на выполнение.

```json
{
  "languages": [
    {"id": "python", "title": "Python", "description": "..."},
    {"id": "javascript", "title": "JavaScript", "description": "..."}
  ]
}
```

---

## Execute (sync)

```
POST /api/v1/execute
```

**Тело запроса:**

| Поле | Тип | Default | Описание |
|---|---|---|---|
| `code` | string | — | Код для запуска |
| `lang` | string | — | Язык из `GET /languages` |
| `timeout` | int | 30 | Макс. время выполнения (сек) |
| `memory` | int | 256 | Макс. память (МБ) |
| `cpu` | float | 1.0 | Макс. CPU |
| `network` | bool | false | Доступ к сети (не передаётся в sandbox) |
| `files` | object | `{}` | Файлы `{"path": "содержимое"}` |

**Ответ:**

```json
{
  "status": "success",
  "stdout": "2\n",
  "stderr": "",
  "exit_code": 0
}
```

Возможные значения `status`: `success`, `error`, `timeout`.

---

## Execute (async)

**Создать задачу:**

```
POST /api/v1/execute/async
Body: (то же что sync)
```

```json
{"id": "uuid"}
```

**Получить результат:**

```
GET /api/v1/execute/async/{id}
```

```json
{
  "status": "pending",
  "stdout": "",
  "stderr": "",
  "exit_code": 0
}
```

Возможные значения `status`: `pending`, `finish`, `error`, `timeout`.

---

## Sessions

Stateful-сессия с сохранением состояния между вызовами (Python).

**Создать сессию:**

```
POST /api/v1/sessions
Body: {"ttl": 1800, "memory": 512, "cpu": 1.0}
```

**Выполнить код:**

```
POST /api/v1/sessions/{id}/execute
Body: {"code": "x = 1"}
```

**Загрузить файлы:**

```
POST /api/v1/sessions/{id}/files
Body: {"files": {"data.csv": "...", "utils/helper.py": "..."}}
```

**Список файлов:**

```
GET /api/v1/sessions/{id}/files
```

**Завершить сессию:**

```
POST /api/v1/sessions/{id}/finish
```

---

## Ошибки

| HTTP | `error` | Причина |
|---|---|---|
| 400 | `path_traversal` | Недопустимый путь в `files` |
| 404 | `not_found` | Async-задача не найдена |
| 404 | `invalid_env` | Сессия не найдена |
| 503 | `overloaded` | Превышен лимит одновременных запросов |
| 502 | `sandbox_error` | Ошибка на стороне SandboxFusion |

```json
{
  "error": "overloaded",
  "message": "Too many concurrent executions"
}
```
