from typing import Any, Optional

from pydantic import BaseModel, Field


class ExecuteRequest(BaseModel):
    code: str = Field(..., description="Code to execute")
    lang: str = Field(..., description="Language (python, nodejs, etc)")
    timeout: int = Field(30, ge=1, description="Execution timeout in seconds")
    memory: int = Field(256, ge=1, description="Memory limit in MB")
    cpu: float = Field(1.0, ge=0.1, description="CPU limit")
    network: bool = Field(False, description="Enable network")
    env: Optional[str] = Field(None, description="Environment ID from registry")
    files: dict[str, str] = Field(default_factory=dict, description="path -> base64 content")


class ExecuteResponse(BaseModel):
    status: str = Field(..., description="success|timeout|error|memory_limit")
    stdout: str = Field("", description="Standard output")
    stderr: str = Field("", description="Standard error")
    exit_code: int = Field(0, description="Process exit code")


class ExecuteAsyncResponse(BaseModel):
    id: str = Field(..., description="Task ID for polling")


class ExecuteAsyncStatusResponse(BaseModel):
    status: str = Field(..., description="pending|timeout|finish")
    stdout: str = Field("", description="Standard output when finish")
    stderr: str = Field("", description="Standard error when finish")
    exit_code: int = Field(0, description="Exit code when finish")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human readable message")
    details: Optional[dict[str, Any]] = Field(None, description="Additional details")
