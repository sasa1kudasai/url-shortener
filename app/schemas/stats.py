from datetime import date
from pydantic import BaseModel


class ClicksByDay(BaseModel):
    day: date
    count: int


class DeviceStats(BaseModel):
    device_type: str
    count: int


class StatsResponse(BaseModel):
    short_code: str
    long_url: str
    total_clicks: int
    clicks_by_day: list[ClicksByDay]
    clicks_by_device: list[DeviceStats]