import httpx
from fastapi import APIRouter, HTTPException

from app.models.schemas import SessionCreate, SessionExecute, SessionFiles
from app.services.sandbox_fusion import sandbox_client
from app.utils.path_validation import validate_paths

router = APIRouter(prefix="/api/v1", tags=["sessions"])


def _session_error(exc: httpx.HTTPStatusError) -> HTTPException:
    if exc.response.status_code == 404:
        return HTTPException(404, {"error": "invalid_env", "message": "Session not found"})
    return HTTPException(502, {"error": "sandbox_error", "message": str(exc)})


@router.post("/sessions")
async def session_create(req: SessionCreate):
    try:
        return await sandbox_client.create_session(req.ttl, req.memory)
    except httpx.HTTPStatusError as exc:
        raise _session_error(exc) from exc


@router.post("/sessions/{session_id}/execute")
async def session_execute(session_id: str, req: SessionExecute):
    try:
        return await sandbox_client.run_in_session(session_id, req.code)
    except httpx.HTTPStatusError as exc:
        raise _session_error(exc) from exc


@router.post("/sessions/{session_id}/files")
async def session_upload_files(session_id: str, req: SessionFiles):
    path_err = validate_paths(req.files)
    if path_err:
        raise HTTPException(
            status_code=400,
            detail={"error": "path_traversal", "message": "Invalid file path", "details": {"reason": path_err}},
        )
    try:
        return await sandbox_client.upload_session_files(session_id, req.files)
    except httpx.HTTPStatusError as exc:
        raise _session_error(exc) from exc


@router.get("/sessions/{session_id}/files")
async def session_list_files(session_id: str):
    try:
        return await sandbox_client.list_session_files(session_id)
    except httpx.HTTPStatusError as exc:
        raise _session_error(exc) from exc


@router.post("/sessions/{session_id}/finish")
async def session_finish(session_id: str):
    try:
        return await sandbox_client.close_session(session_id)
    except httpx.HTTPStatusError as exc:
        raise _session_error(exc) from exc
