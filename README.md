# Code Executor

HTTP-сервис для запуска LLM-кода. Делегирует выполнение [SandboxFusion](sandbox-fusion/) (git submodule), хранит статусы async-задач в Redis.

## Быстрый старт

```bash
git submodule update --init --recursive
docker compose -f docker/docker-compose.yml up -d
```

Сервис доступен на `http://localhost:8000`.

## Тесты

**Unit-тесты** (без SandboxFusion, всё замокано):
```bash
docker compose -f docker/docker-compose.test.yml run --rm test-unit
```

**Стресс-тесты** (поднимает весь стек; первый билд долгий из-за Lean и других рантаймов):
```bash
docker compose -f docker/docker-compose.test.yml up -d redis sandbox-fusion app
docker compose -f docker/docker-compose.test.yml run --rm test-stress
```

**Smoke-тесты** по языкам против живого API:
```bash
docker compose -f docker/docker-compose.test.yml run --rm \
  -e BASE_URL=http://app:8000 -e RUN_DEPLOYED_SMOKE=1 \
  test-unit pytest tests/test_smoke.py -v
```

Остановка: `docker compose -f docker/docker-compose.test.yml down`

## Структура

```
app/
├── api/
│   ├── execute.py        # /execute, /execute/async
│   ├── sessions.py       # /sessions
│   └── system.py         # /health, /languages
├── models/
│   ├── languages.py      # список языков, маппинг → sandbox id
│   └── schemas.py        # Pydantic-схемы
├── services/
│   ├── sandbox_fusion.py # HTTP-клиент к SandboxFusion
│   └── queue.py          # Redis (статусы async-задач)
├── utils/
│   └── path_validation.py
├── config.py
└── main.py
```

## Документация

- [API Reference](docs/api.md)
- [Конфигурация](docs/config.md)
