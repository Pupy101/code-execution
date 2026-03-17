from typing import Any, Literal

from pydantic import BaseModel, Field

# Supported languages from SandboxFusion (sandbox/runners/types.py).
# CPU: python, cpp, nodejs, go, go_test, java, php, csharp, bash, typescript, sql, rust, lua, R, perl, D_ut,
#      ruby, scala, julia, pytest, junit, kotlin_script, jest, verilog, lean, swift, racket
# GPU: cuda, python_gpu
SupportedLanguage = Literal[
    "python",
    "cpp",
    "nodejs",
    "go",
    "go_test",
    "java",
    "php",
    "csharp",
    "bash",
    "typescript",
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

# Languages supported without custom Docker image (built-in runners only).
# sql requires custom image; cuda/python_gpu require GPU runtime.
SUPPORTED_LANGUAGES_DEFAULT: tuple[str, ...] = (
    "python",
    "cpp",
    "nodejs",
    "go",
    "go_test",
    "java",
    "php",
    "csharp",
    "bash",
    "typescript",
    "rust",
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
    "lean",
    "swift",
    "racket",
    "cuda",
    "python_gpu",
)


class ExecuteRequest(BaseModel):
    code: str = Field(..., description="Code to execute")
    lang: SupportedLanguage = Field(
        ...,
        description="Programming language. See SUPPORTED_LANGUAGES_DEFAULT for built-in runners.",
    )
    timeout: int = Field(30, ge=1, description="Execution timeout in seconds")
    memory: int = Field(256, ge=1, description="Memory limit in MB")
    cpu: float = Field(1.0, ge=0.1, description="CPU limit")
    network: bool = Field(False, description="Enable network")
    env: str | None = Field(None, description="Environment ID from registry")
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
