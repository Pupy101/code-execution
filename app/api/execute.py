import asyncio
import uuid
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models.languages import resolve_lang
from app.models.schemas import (
    ExecuteAsyncResponse,
    ExecuteAsyncStatusResponse,
    ExecuteRequest,
    ExecuteResponse,
)
from app.services.queue import job_get, job_set
from app.services.sandbox_fusion import sandbox_client
from app.utils.path_validation import validate_paths

router = APIRouter(prefix="/api/v1", tags=["execute"])

_sandbox_sem = asyncio.Semaphore(settings.MAX_QUEUE_SIZE)

_STATUS_MAP = {"Success": "success", "Failed": "error", "SandboxError": "error"}


def _limits(req: ExecuteRequest) -> tuple[int, int]:
    return min(req.timeout, settings.MAX_TIMEOUT), min(req.memory, settings.MAX_MEMORY)


def _parse_response(data: dict[str, Any]) -> ExecuteResponse:
    run = data.get("run_result") or {}
    compile_ = data.get("compile_result") or {}
    if run.get("status") == "TimeLimitExceeded" or compile_.get("status") == "TimeLimitExceeded":
        status = "timeout"
    elif run.get("status") == "Error":
        status = "error"
    else:
        status = _STATUS_MAP.get(data.get("status", ""), "error")
    stdout = run.get("stdout") or ""
    stderr = run.get("stderr") or ""
    exit_code = run.get("return_code") or 0
    if not run and compile_:
        stderr = compile_.get("stderr") or stderr
        exit_code = compile_.get("return_code") or exit_code
    return ExecuteResponse(status=status, stdout=stdout, stderr=stderr, exit_code=exit_code)


async def _run(req: ExecuteRequest, timeout: int, memory: int) -> ExecuteResponse:
    lang = resolve_lang(req.lang)
    async with _sandbox_sem:
        try:
            data = await sandbox_client.run_code(
                code=req.code,
                language=lang,
                compile_timeout=timeout,
                run_timeout=timeout,
                memory_limit_MB=memory,
                files=dict(req.files) or {},
            )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=502, detail={"error": "sandbox_error", "message": str(exc)}) from exc
        except httpx.TimeoutException:
            return ExecuteResponse(status="timeout", stdout="", stderr="SandboxFusion request timed out", exit_code=-1)
    return _parse_response(data)


@router.post("/execute", response_model=ExecuteResponse)
async def execute(req: ExecuteRequest) -> ExecuteResponse:
    path_err = validate_paths(req.files)
    if path_err:
        raise HTTPException(
            status_code=400,
            detail={"error": "path_traversal", "message": "Invalid file path", "details": {"reason": path_err}},
        )
    if _sandbox_sem.locked():
        raise HTTPException(
            status_code=503,
            detail={"error": "overloaded", "message": "Too many concurrent executions"},
        )
    timeout, memory = _limits(req)
    return await _run(req, timeout, memory)


async def _run_job(job_id: str, req: ExecuteRequest, timeout: int, memory: int) -> None:
    try:
        result = await _run(req, timeout, memory)
        job_set(job_id, {"status": "finish", **result.model_dump()})
    except Exception as exc:
        job_set(job_id, {"status": "error", "stdout": "", "stderr": str(exc), "exit_code": -1})


@router.post("/execute/async", response_model=ExecuteAsyncResponse)
async def execute_async(req: ExecuteRequest) -> ExecuteAsyncResponse:
    path_err = validate_paths(req.files)
    if path_err:
        raise HTTPException(
            status_code=400,
            detail={"error": "path_traversal", "message": "Invalid file path", "details": {"reason": path_err}},
        )
    if _sandbox_sem.locked():
        raise HTTPException(
            status_code=503,
            detail={"error": "overloaded", "message": "Too many concurrent executions"},
        )
    timeout, memory = _limits(req)
    job_id = str(uuid.uuid4())
    job_set(job_id, {"status": "pending", "stdout": "", "stderr": "", "exit_code": 0})
    task = asyncio.create_task(_run_job(job_id, req, timeout, memory))
    task.add_done_callback(lambda t: t.exception() if not t.cancelled() else None)
    return ExecuteAsyncResponse(id=job_id)


@router.get("/execute/async/{job_id}", response_model=ExecuteAsyncStatusResponse)
async def get_job_status(job_id: str) -> ExecuteAsyncStatusResponse:
    data = job_get(job_id)
    if data is None:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Job not found"})
    return ExecuteAsyncStatusResponse(
        status=data.get("status", "pending"),
        stdout=data.get("stdout", ""),
        stderr=data.get("stderr", ""),
        exit_code=data.get("exit_code", 0),
    )
