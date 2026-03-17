from typing import Any, Optional

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
            except Exception:
                return False

    async def run_code(
        self,
        code: str,
        language: str,
        *,
        compile_timeout: float = 10,
        run_timeout: float = 10,
        memory_limit_MB: int = -1,
        stdin: Optional[str] = None,
        files: dict[str, Optional[str]] | None = None,
        fetch_files: list[str] | None = None,
        image: Optional[str] = None,
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
            return r.json()


sandbox_client = SandboxFusionClient()
