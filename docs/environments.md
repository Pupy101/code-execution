# Environments

## Сборка Docker-образов

Среды собираются вне приложения. Пример Dockerfile:

```dockerfile
FROM python:3.11-slim
RUN pip install numpy pandas
```

Соберите и запушьте образ в registry:

```bash
docker build -t my-registry/ml-env:v1 .
docker push my-registry/ml-env:v1
```

## Регистрация

После сборки зарегистрируйте среду через API:

```bash
curl -X POST http://localhost:8000/api/v1/environments \
  -H "Content-Type: application/json" \
  -d '{
    "id": "ml-python",
    "image": "my-registry/ml-env:v1",
    "lang": "python",
    "desc": "Python + numpy, pandas"
  }'
```

## Использование

При вызове `POST /api/v1/execute` укажите `env`:

```json
{
  "code": "import numpy; print(numpy.__version__)",
  "lang": "python",
  "env": "ml-python"
}
```

Для сессий укажите `env` при создании:

```json
{
  "ttl": 1800,
  "env": "ml-python",
  "memory": 512
}
```

## Хранение

Среды хранятся в `config/environments/{id}.yaml`. Удобно для GitOps.
