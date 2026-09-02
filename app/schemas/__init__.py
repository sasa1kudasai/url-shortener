from app.schemas.url import URLCreate, URLResponse
from app.schemas.stats import ClicksByDay, DeviceStats, StatsResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.dashboard import DashboardResponse, RecentLink


__all__ = ["URLCreate", "URLResponse", "ClicksByDay", "DeviceStats", "StatsResponse",
           "UserCreate", "UserLogin", "UserResponse", "TokenResponse",
           "DashboardResponse", "RecentLink"]