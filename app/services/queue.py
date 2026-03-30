import json
from typing import Any

import redis

from app.config import settings

_JOB_PREFIX = "job:"


def get_redis() -> redis.Redis:
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def job_set(job_id: str, data: dict[str, Any]) -> None:
    get_redis().setex(f"{_JOB_PREFIX}{job_id}", settings.TASK_TTL, json.dumps(data))


def job_get(job_id: str) -> dict[str, Any] | None:
    raw = get_redis().get(f"{_JOB_PREFIX}{job_id}")
    if raw is None:
        return None
    result: dict[str, Any] = json.loads(raw)
    return result
