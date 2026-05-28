from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from app.config import settings

_code_length = settings.short_code_length


class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_code: str | None = Field(
        default=None,
        min_length=_code_length,
        max_length=_code_length,
    )

class ShortenResponse(BaseModel):
    code: str = Field(min_length=_code_length, max_length=_code_length)
    short_url: str
    original_url: str
    message: str

class LinkApiModel(BaseModel):
    """Public link shape returned from API routes."""

    code: str = Field(min_length=_code_length, max_length=_code_length)
    url: HttpUrl

class StoredLink(BaseModel):
    """Full link record persisted in data/links.json."""

    code: str = Field(min_length=_code_length, max_length=_code_length)
    url: HttpUrl
    url_hash: str | None = None
    created_at: datetime
