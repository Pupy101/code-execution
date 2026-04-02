from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.languages import LANGUAGE_IDS

Language = Literal[*LANGUAGE_IDS]  # type: ignore


class ExecuteRequest(BaseModel):
    code: str
    lang: Language
    timeout: int = Field(30, ge=1)
    memory: int = Field(256, ge=1)
    cpu: float = Field(1.0, ge=0.1)
    network: bool = False
    files: dict[str, str] = Field(default_factory=dict)


class ExecuteResult(BaseModel):
    status: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0


class ExecuteResponse(ExecuteResult):
    pass


class ExecuteAsyncResponse(BaseModel):
    id: str


class ExecuteAsyncStatusResponse(ExecuteResult):
    pass


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict[str, Any] | None = None


class LanguageItem(BaseModel):
    id: str
    title: str
    description: str


class LanguagesResponse(BaseModel):
    languages: list[LanguageItem]


class SessionCreate(BaseModel):
    ttl: int = 1800
    memory: int = 512
    cpu: float = 1.0


class SessionExecute(BaseModel):
    code: str


class SessionFiles(BaseModel):
    files: dict[str, str]
