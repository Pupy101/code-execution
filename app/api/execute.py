import time
from typing import Any

from fastapi import APIRouter, HTTPException
from rq.job import Job

from app.config import settings
from app.models.schemas import (
    ExecuteAsyncResponse,
    ExecuteAsyncStatusResponse,
    ExecuteRequest,
    ExecuteResponse,
)
from app.services.queue import enqueue, get_queue_len, get_redis
from app.utils.path_validation import validate_paths
from app.workers.tasks import run_execute_task

router = APIRouter(prefix="/api/v1", tags=["execute"])


def _apply_limits(req: ExecuteRequest) -> tuple[int, int, float]:
    timeout = min(req.timeout, settings.MAX_TIMEOUT)
    memory = min(req.memory, settings.MAX_MEMORY)
    cpu = min(req.cpu, settings.MAX_CPU)
    return timeout, memory, cpu


@router.post("/execute", response_model=ExecuteResponse)
async def execute_sync(req: ExecuteRequest) -> ExecuteResponse:
    path_err = validate_paths(req.files)
    if path_err:
        raise HTTPException(
            status_code=400,
            detail={"error": "path_traversal", "message": "Invalid file path", "details": {"reason": path_err}},
        )
    if get_queue_len() >= settings.MAX_QUEUE_SIZE:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "queue_full",
                "message": "Queue is full",
                "details": {"queue_len": get_queue_len(), "max": settings.MAX_QUEUE_SIZE},
            },
        )
    timeout, memory, _ = _apply_limits(req)
    submitted_at = time.time()
    job_id = enqueue(
        run_execute_task,
        req.code,
        req.lang,
        timeout,
        memory,
        req.env,
        req.files,
        submitted_at,
    )
    if not job_id:
        raise HTTPException(status_code=503, detail={"error": "queue_full", "message": "Failed to enqueue"})
    redis_conn = get_redis()
    poll_interval = 0.5
    http_timeout = min(timeout + 60, 330)
    deadline = time.time() + http_timeout
    while time.time() < deadline:
        job = Job.fetch(job_id, connection=redis_conn)
        if job.is_finished:
            result = job.result
            if result is None:
                result = {"status": "error", "stdout": "", "stderr": "Unknown error", "exit_code": -1}
            return ExecuteResponse(**result)
        if job.is_failed:
            return ExecuteResponse(
                status="error",
                stdout="",
                stderr=str(job.exc_info) if job.exc_info else "Job failed",
                exit_code=-1,
            )
        time.sleep(poll_interval)
    return ExecuteResponse(
        status="timeout",
        stdout="",
        stderr="HTTP request timeout",
        exit_code=-1,
    )


@router.post("/execute/async", response_model=ExecuteAsyncResponse)
async def execute_async(req: ExecuteRequest) -> ExecuteAsyncResponse:
    path_err = validate_paths(req.files)
    if path_err:
        raise HTTPException(
            status_code=400,
            detail={"error": "path_traversal", "message": "Invalid file path", "details": {"reason": path_err}},
        )
    if get_queue_len() >= settings.MAX_QUEUE_SIZE:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "queue_full",
                "message": "Queue is full",
                "details": {"queue_len": get_queue_len(), "max": settings.MAX_QUEUE_SIZE},
            },
        )
    timeout, memory, _ = _apply_limits(req)
    submitted_at = time.time()
    job_id = enqueue(
        run_execute_task,
        req.code,
        req.lang,
        timeout,
        memory,
        req.env,
        req.files,
        submitted_at,
    )
    if not job_id:
        raise HTTPException(status_code=503, detail={"error": "queue_full", "message": "Failed to enqueue"})
    return ExecuteAsyncResponse(id=job_id)


@router.get("/execute/async/{job_id}", response_model=ExecuteAsyncStatusResponse)
async def get_execute_async_status(job_id: str) -> ExecuteAsyncStatusResponse:
    try:
        job = Job.fetch(job_id, connection=get_redis())
    except Exception:
        raise HTTPException(status_code=404, detail={"error": "validation_error", "message": "Job not found"})
    if job.is_queued or job.is_started:
        return ExecuteAsyncStatusResponse(status="pending", stdout="", stderr="", exit_code=0)
    if job.is_failed:
        return ExecuteAsyncStatusResponse(
            status="timeout",
            stdout="",
            stderr=str(job.exc_info) if job.exc_info else "Job failed",
            exit_code=-1,
        )
    result: dict[str, Any] = job.result or {}
    return ExecuteAsyncStatusResponse(
        status="finish",
        stdout=result.get("stdout", ""),
        stderr=result.get("stderr", ""),
        exit_code=result.get("exit_code", 0),
    )
