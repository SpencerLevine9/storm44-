"""Pydantic schemas for user account API (username / password)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserAccountCreate(BaseModel):
    """Payload for creating a user account. Hash the password before storing."""

    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1)


class UserAccountInDB(BaseModel):
    """User account as stored (id, username, no password)."""

    id: int
    username: str
    created_at: str | None = None

    class Config:
        from_attributes = True
