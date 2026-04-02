from typing import Any, Literal

from pydantic import BaseModel, Field

# Mirrors sandbox.runners.types.Language — values accepted by SandboxFusion POST /run_code.
SupportedLanguage = Literal[
    "python",
    "cpp",
    "nodejs",
    "js",
    "go",
    "go_test",
    "java",
    "php",
    "csharp",
    "bash",
    "typescript",
    "ts",
    "sql",
    "rust",
    "cuda",
    "lua",
    "R",
    "perl",
    "D_ut",
    "ruby",
    "scala",
    "julia",
    "pytest",
    "junit",
    "kotlin_script",
    "jest",
    "verilog",
    "python_gpu",
    "lean",
    "swift",
    "racket",
]


class ExecuteRequest(BaseModel):
    code: str = Field(..., description="Code to execute")
    lang: SupportedLanguage = Field(
        ...,
        description="Language id for SandboxFusion run_code (sandbox.runners.types.Language + CODE_RUNNERS keys).",
    )
    timeout: int = Field(30, ge=1, description="Execution timeout in seconds")
    memory: int = Field(256, ge=1, description="Memory limit in MB")
    cpu: float = Field(1.0, ge=0.1, description="CPU limit")
    network: bool = Field(False, description="Enable network")
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
    details: dict[str, Any] | None = Field(None, description="Additional details")
