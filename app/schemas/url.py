from pydantic import BaseModel, HttpUrl, ConfigDict


class URLCreate(BaseModel):
    long_url: HttpUrl


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