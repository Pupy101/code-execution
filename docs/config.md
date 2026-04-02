# Конфигурация

Настраивается через переменные окружения или файл `.env` в корне репозитория.

## Переменные

| Переменная | Default | Описание |
|---|---|---|
| `SANDBOX_FUSION_URL` | `http://sandbox-fusion:8080` | URL SandboxFusion |
| `REDIS_URL` | `redis://localhost:6379/0` | URL Redis |
| `MAX_TIMEOUT` | `300` | Макс. время выполнения (сек) |
| `MAX_MEMORY` | `4096` | Макс. память (МБ) |
| `MAX_CPU` | `4.0` | Макс. CPU |
| `MAX_QUEUE_SIZE` | `500` | Макс. число одновременных запросов к sandbox |
| `TASK_TTL` | `1800` | Время хранения результата async-задачи в памяти (сек) |

## Лимиты запросов

Значения `timeout`, `memory`, `cpu` из запроса клиента урезаются до соответствующего `MAX_*`:

```
effective = min(user_value, MAX_*)
```

При превышении `MAX_QUEUE_SIZE` одновременных запросов возвращается `503 overloaded`.
