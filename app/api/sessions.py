from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.utils.path_validation import validate_paths

router = APIRouter(prefix="/api/v1", tags=["sessions"])

SANDBOX_URL = settings.SANDBOX_FUSION_URL.rstrip("/")


class SessionCreateRequest(BaseModel):
    ttl: int = Field(1800, description="Seconds of inactivity before auto-finish")
    memory: int = Field(512, description="Memory limit MB")
    cpu: float = Field(1.0, description="CPU limit")


class SessionExecuteRequest(BaseModel):
    code: str = Field(..., description="Code to execute")


class SessionFilesRequest(BaseModel):
    files: dict[str, str] = Field(..., description="path -> base64 content")


@router.post("/sessions")
async def session_create(req: SessionCreateRequest):
    payload: dict[str, Any] = {"ttl": req.ttl, "memory": req.memory, "cpu": req.cpu}
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{SANDBOX_URL}/sessions", json=payload)
        r.raise_for_status()
        return r.json()


@router.post("/sessions/{session_id}/execute")
async def session_execute(session_id: str, req: SessionExecuteRequest):
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(f"{SANDBOX_URL}/sessions/{session_id}/execute", json={"code": req.code})
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail={"error": "invalid_env", "message": "Session not found"})
        r.raise_for_status()
        return r.json()


@router.post("/sessions/{session_id}/files")
async def session_upload_files(session_id: str, req: SessionFilesRequest):
    path_err = validate_paths(req.files)
    if path_err:
        raise HTTPException(
            status_code=400,
            detail={"error": "path_traversal", "message": "Invalid file path", "details": {"reason": path_err}},
        )
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{SANDBOX_URL}/sessions/{session_id}/files", json={"files": req.files})
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail={"error": "invalid_env", "message": "Session not found"})
        r.raise_for_status()
        return r.json()


@router.get("/sessions/{session_id}/files")
async def session_list_files(session_id: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SANDBOX_URL}/sessions/{session_id}/files")
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail={"error": "invalid_env", "message": "Session not found"})
        r.raise_for_status()
        return r.json()


@router.post("/sessions/{session_id}/finish")
async def session_finish(session_id: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{SANDBOX_URL}/sessions/{session_id}/finish")
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail={"error": "invalid_env", "message": "Session not found"})
        r.raise_for_status()
        return r.json()
