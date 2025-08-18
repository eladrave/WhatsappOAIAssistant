from contextlib import asynccontextmanager

from fastapi import FastAPI
import httpx

from .router_health import router as health_router
from .router_webhook import router as webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    timeout = httpx.Timeout(60.0, connect=20.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        app.state.http_client = client
        yield


app = FastAPI(lifespan=lifespan)
app.include_router(health_router)
app.include_router(webhook_router)
