from fastapi import APIRouter

from app.models.languages import lang_metadata
from app.models.schemas import LanguageItem, LanguagesResponse

router = APIRouter(tags=["system"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/languages", response_model=LanguagesResponse)
async def list_languages():
    return LanguagesResponse(languages=[LanguageItem(**row) for row in lang_metadata()])
