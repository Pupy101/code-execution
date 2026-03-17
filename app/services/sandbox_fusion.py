from typing import Any

import httpx

from app.config import settings


class SandboxFusionClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.SANDBOX_FUSION_URL).rstrip("/")

    async def health(self) -> bool:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                r = await client.get(f"{self.base_url}/health")
                return r.status_code == 200
            except httpx.HTTPError:
                return False

    async def run_code(
        self,
        code: str,
        language: str,
        *,
        compile_timeout: float = 10,
        run_timeout: float = 10,
        memory_limit_MB: int = -1,
        stdin: str | None = None,
        files: dict[str, str | None] | None = None,
        fetch_files: list[str] | None = None,
        image: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": code,
            "language": language,
            "compile_timeout": compile_timeout,
            "run_timeout": run_timeout,
            "memory_limit_MB": memory_limit_MB,
            "files": files or {},
            "fetch_files": fetch_files or [],
        }
        if stdin is not None:
            payload["stdin"] = stdin
        if image:
            payload["image"] = image
        async with httpx.AsyncClient(timeout=run_timeout + 30) as client:
            r = await client.post(f"{self.base_url}/run_code", json=payload)
            r.raise_for_status()
            result: dict[str, Any] = r.json()
            return result


sandbox_client = SandboxFusionClient()
