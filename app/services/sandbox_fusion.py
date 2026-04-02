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
        async with httpx.AsyncClient(timeout=run_timeout + 30) as client:
            r = await client.post(f"{self.base_url}/run_code", json=payload)
            r.raise_for_status()
            result: dict[str, Any] = r.json()
            return result

    async def create_session(self, ttl: int, memory: int, cpu: float) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                f"{self.base_url}/sessions",
                json={"ttl": ttl, "memory": memory, "cpu": cpu},
            )
            r.raise_for_status()
            return r.json()  # type: ignore

    async def run_in_session(self, session_id: str, code: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(
                f"{self.base_url}/sessions/{session_id}/execute",
                json={"code": code},
            )
            r.raise_for_status()
            return r.json()  # type: ignore

    async def upload_session_files(self, session_id: str, files: dict[str, str]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f"{self.base_url}/sessions/{session_id}/files",
                json={"files": files},
            )
            r.raise_for_status()
            return r.json()  # type: ignore

    async def list_session_files(self, session_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.base_url}/sessions/{session_id}/files")
            r.raise_for_status()
            return r.json()  # type: ignore

    async def close_session(self, session_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{self.base_url}/sessions/{session_id}/finish")
            r.raise_for_status()
            return r.json()  # type: ignore


sandbox_client = SandboxFusionClient()
