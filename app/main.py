from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.environments import router as environments_router
from app.api.execute import router as execute_router
from app.api.sessions import router as sessions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(execute_router)
app.include_router(environments_router)
app.include_router(sessions_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
