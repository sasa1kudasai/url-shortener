import re

from fastapi import HTTPException
from pydantic import BaseModel, HttpUrl, ConfigDict, field_validator


class URLCreate(BaseModel):
    long_url: HttpUrl
    custom_alias: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, value:str | None) -> str | None:
        if value is None or value.strip() == "":
            return None
        if not re.fullmatch(r"[a-zA-Z0-9_-]{3,20}", value):
            raise ValueError("Invalid alias format")
        return value


class URLResponse(BaseModel):
    short_code: str
    long_url: str
    click_count: int
    owner_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedLinksResponse(BaseModel):
    items: list[URLResponse]
    total: int
    page: int
    page_size: int
    total_pages: int