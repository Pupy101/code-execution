# Code Executor

HTTP-приложение для исполнения LLM-кода на базе SandboxFusion.

## Возможности

- **Sync/Async execute** — выполнение кода (SandboxFusion + Redis для статусов async-задач)
- **Сессии (Python)** — stateful-сессии: create, execute, files, finish (образ сессии задаётся в SandboxFusion)
- **Fork SandboxFusion** — `run_code` по языкам из встроенных раннеров, healthcheck

## Быстрый старт

```bash
# Клонирование submodule (sandbox-fusion)
git submodule update --init --recursive

# Запуск стека (Redis + SandboxFusion + приложение), из корня репозитория
docker compose -f docker/docker-compose.yml up -d
```

API доступен на `http://localhost:8000`. SandboxFusion снаружи: `http://localhost:9090`. Остановка: `docker compose -f docker/docker-compose.yml down`.

Документация:

- [API Reference](docs/api.md)
- [Configuration](docs/config.md)

### Тесты в Docker

**Быстрые unit-тесты** (без SandboxFusion, моки HTTP/Redis):

```bash
docker compose -f docker/docker-compose.test.yml run --rm test-unit
```

**Интеграция + стресс** (поднимает Redis, SandboxFusion и приложение; первый билд образа sandbox может занять много времени из‑за сборки окружения Lean и др.):

```bash
docker compose -f docker/docker-compose.test.yml up -d redis sandbox-fusion app
docker compose -f docker/docker-compose.test.yml run --rm test-stress
```

**Smoke по языкам** против поднятого API (из контейнера с тестами):

```bash
docker compose -f docker/docker-compose.test.yml run --rm \
  -e BASE_URL=http://app:8000 -e RUN_DEPLOYED_SMOKE=1 \
  test-unit pytest tests/test_smoke.py -v
```

Остановка стека: `docker compose -f docker/docker-compose.test.yml down`.

## Структура

```
code-executor/
├── app/              # FastAPI приложение
├── sandbox-fusion/   # Fork SandboxFusion
└── docs/             # Документация
```
