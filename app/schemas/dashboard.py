from pydantic import BaseModel, ConfigDict


class RecentLink(BaseModel):
    short_code: str
    long_url: str
    click_count: int

    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(BaseModel):
    total_clicks: int
    active_links: int
    avg_clicks_per_day: float
    recent_links: list[RecentLink]

    