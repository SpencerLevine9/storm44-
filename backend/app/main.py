import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.database.database import close_pool, get_db, init_db  # noqa: E402
from app.api.v1.router import api_router

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    print("Database tables initialised.")
    yield
    close_pool()
    print("Connection pool closed.")


app = FastAPI(title="Storm44 Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
    return {"status": "ok", "database": "connected"}

app.include_router(api_router, prefix="/api/v1")
