import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.db.database import init_pool, close_pool  # noqa: E402
from app.api.v1.router import api_router

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_pool()
    print("Database pool initialised.")
    import asyncio
    from machine_learning.ingest_pipeline.store.retrieve import embed_query_local
    await asyncio.get_event_loop().run_in_executor(None, embed_query_local, "warmup")
    print("Embedding model warmed up.")
    yield
    await close_pool()
    print("Connection pool closed.")


app = FastAPI(title="Storm44 Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
