import time
from typing import Any

import httpx

from app.config import settings
from app.services.env_registry import get_env_image


def run_execute_task(
    code: str,
    lang: str,
    timeout: int,
    memory: int,
    env_id: str | None,
    files: dict[str, str],
    submitted_at: float,
) -> dict[str, Any]:
    if time.time() - submitted_at > settings.QUEUE_TIMEOUT:
        return {
            "status": "timeout",
            "stdout": "",
            "stderr": "Task exceeded queue timeout",
            "exit_code": -1,
        }
    timeout_eff = min(timeout, settings.MAX_TIMEOUT)
    memory_eff = min(memory, settings.MAX_MEMORY)
    image = get_env_image(env_id) if env_id else None
    files_decoded: dict[str, str | None] = dict(files.items())
    with httpx.Client(timeout=timeout_eff + 30) as http_client:
        payload: dict[str, Any] = {
            "code": code,
            "language": lang,
            "compile_timeout": timeout_eff,
            "run_timeout": timeout_eff,
            "memory_limit_MB": memory_eff,
            "files": files_decoded,
        }
        if image:
            payload["image"] = image
        r = http_client.post(
            f"{settings.SANDBOX_FUSION_URL.rstrip('/')}/run_code",
            json=payload,
        )
        r.raise_for_status()
        data = r.json()
    status_map = {"Success": "success", "Failed": "error", "SandboxError": "error"}
    run = data.get("run_result") or {}
    if run.get("status") == "TimeLimitExceeded":
        status = "timeout"
    elif run.get("status") == "Error":
        status = "error"
    else:
        status = status_map.get(data.get("status", ""), "error")
    return {
        "status": status,
        "stdout": run.get("stdout") or "",
        "stderr": run.get("stderr") or "",
        "exit_code": run.get("return_code", 0) or 0,
    }
