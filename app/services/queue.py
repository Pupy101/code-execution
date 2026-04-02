import time
from typing import Any

from app.config import settings

_jobs: dict[str, tuple[float, dict[str, Any]]] = {}


def job_set(job_id: str, data: dict[str, Any]) -> None:
    _jobs[job_id] = (time.monotonic() + settings.TASK_TTL, data)
    _evict()


def job_get(job_id: str) -> dict[str, Any] | None:
    entry = _jobs.get(job_id)
    if entry is None:
        return None
    expires_at, data = entry
    if time.monotonic() > expires_at:
        del _jobs[job_id]
        return None
    return data


def _evict() -> None:
    now = time.monotonic()
    expired = [k for k, (exp, _) in _jobs.items() if exp < now]
    for k in expired:
        del _jobs[k]
