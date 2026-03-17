from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.env_registry import (
    delete_environment,
    list_environments,
    register_environment,
    update_environment,
)

router = APIRouter(prefix="/api/v1", tags=["environments"])


class EnvRegisterRequest(BaseModel):
    id: str = Field(..., description="Environment ID")
    image: str = Field(..., description="Docker image")
    lang: str = Field("", description="Language")
    desc: str = Field("", description="Description")


class EnvUpdateRequest(BaseModel):
    image: Optional[str] = Field(None, description="Docker image")
    desc: Optional[str] = Field(None, description="Description")


@router.post("/environments")
async def env_register(req: EnvRegisterRequest):
    result = register_environment(req.id, req.image, req.lang, req.desc)
    return result


@router.get("/environments")
async def env_list():
    envs = list_environments()
    return {"environments": envs}


@router.put("/environments/{env_id}")
async def env_update(env_id: str, req: EnvUpdateRequest):
    result = update_environment(env_id, req.image, req.desc)
    if result is None:
        raise HTTPException(status_code=404, detail={"error": "invalid_env", "message": "Environment not found"})
    return result


@router.delete("/environments/{env_id}")
async def env_delete(env_id: str):
    if not delete_environment(env_id):
        raise HTTPException(status_code=404, detail={"error": "invalid_env", "message": "Environment not found"})
    return {"status": "deleted"}
