from typing import Any, Callable

import redis
from rq import Queue

from app.config import settings


def get_redis() -> redis.Redis:
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)


def get_queue() -> Queue:
    return Queue(connection=get_redis(), default_timeout=settings.TASK_TTL)


def get_queue_len() -> int:
    q = get_queue()
    return len(q)


def enqueue(job_func: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    q = get_queue()
    job = q.enqueue(job_func, *args, **kwargs, job_timeout=settings.TASK_TTL)
    return job.id if job else ""
