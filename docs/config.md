# Configuration

## Переменные окружения

| Переменная | Описание | Default |
|------------|----------|---------|
| MAX_TIMEOUT | Макс. timeout исполнения (сек) | 300 |
| MAX_MEMORY | Макс. память (MB) | 1024 |
| MAX_CPU | Макс. CPU | 4 |
| SANDBOX_FUSION_URL | URL SandboxFusion | http://sandbox-fusion:8080 |
| ENVIRONMENTS_DIR | Директория реестра сред | config/environments |
| WORKER_COUNT | Кол-во RQ workers | 4 |
| MAX_QUEUE_SIZE | Макс. размер очереди | 500 |
| QUEUE_TIMEOUT | Таймаут ожидания в очереди (сек) | 1800 |
| TASK_TTL | TTL задачи (сек) | 1800 |
| REDIS_URL | URL Redis | redis://localhost:6379/0 |

## Лимиты

- `effective = min(user_value, MAX_*)` для timeout, memory, cpu
- При `queue_len >= MAX_QUEUE_SIZE` — 503
- Задача в очереди дольше QUEUE_TIMEOUT — queue_timeout
