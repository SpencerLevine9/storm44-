from collections.abc import AsyncGenerator

import asyncpg

from app.db.database import get_pool


async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    pool = get_pool()
    async with pool.acquire() as conn:
        yield conn
