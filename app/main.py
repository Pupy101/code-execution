from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.execute import router as execute_router
from app.api.sessions import router as sessions_router
from app.api.system import router as system_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(system_router)
app.include_router(execute_router)
app.include_router(sessions_router)
