from pathlib import Path
from typing import Any

import yaml

from app.config import settings


def _env_dir() -> Path:
    return Path(settings.ENVIRONMENTS_DIR)


def _env_path(env_id: str) -> Path:
    return _env_dir() / f"{env_id}.yaml"


def get_env_image(env_id: str) -> str | None:
    path = _env_path(env_id)
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return (data or {}).get("image")


def list_environments() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    d = _env_dir()
    if not d.exists():
        return result
    for p in d.glob("*.yaml"):
        env_id = p.stem
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        result.append(
            {
                "id": env_id,
                "image": data.get("image", ""),
                "lang": data.get("lang", ""),
                "desc": data.get("desc", ""),
            }
        )
    return result


def register_environment(env_id: str, image: str, lang: str = "", desc: str = "") -> dict[str, Any]:
    d = _env_dir()
    d.mkdir(parents=True, exist_ok=True)
    path = _env_path(env_id)
    data = {"id": env_id, "image": image, "lang": lang, "desc": desc}
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    return {"id": env_id, "image": image, "status": "registered"}


def update_environment(env_id: str, image: str | None = None, desc: str | None = None) -> dict[str, Any] | None:
    path = _env_path(env_id)
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if image is not None:
        data["image"] = image
    if desc is not None:
        data["desc"] = desc
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    return {"id": env_id, "image": data.get("image", ""), "status": "updated"}


def delete_environment(env_id: str) -> bool:
    path = _env_path(env_id)
    if path.exists():
        path.unlink()
        return True
    return False
