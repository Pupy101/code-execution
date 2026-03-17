# Code Executor

HTTP-приложение для исполнения LLM-кода на базе SandboxFusion.

## Возможности

- **Sync/Async execute** — выполнение кода через очередь (Redis + RQ)
- **Реестр сред** — регистрация кастомных Docker-образов в `config/environments/`
- **Сессии (Python)** — stateful-сессии: create, execute, files, finish
- **Fork SandboxFusion** — run_code с параметром `image`, sessions, healthcheck

## Быстрый старт

```bash
# Клонирование submodule (sandbox-fusion)
git submodule update --init --recursive

# Запуск через Docker Compose
cd docker && docker compose up -d
```

API доступен на `http://localhost:8000`. Документация:

- [API Reference](docs/api.md)
- [Environments](docs/environments.md)
- [Configuration](docs/config.md)

## Структура

```
code-executor/
├── app/              # FastAPI приложение
├── sandbox-fusion/   # Fork SandboxFusion
├── config/           # Конфигурация
└── docs/             # Документация
```
