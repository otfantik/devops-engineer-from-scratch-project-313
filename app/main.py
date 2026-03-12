from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import links


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    pass


app = FastAPI(title="DevOps Engineer Project", lifespan=lifespan)

app.include_router(links.router, prefix="/api/links", tags=["links"])


@app.get("/ping")
async def ping():
    return "pong"
