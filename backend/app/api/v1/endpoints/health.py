import asyncpg
from fastapi import APIRouter, Depends

from app.api.deps import get_db_connection

router = APIRouter()


@router.get("/health")
async def health_check(conn: asyncpg.Connection = Depends(get_db_connection)):
    await conn.fetchval("SELECT 1")
    return {"status": "ok"}
