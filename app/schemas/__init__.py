from app.schemas.url import URLCreate, URLResponse, PaginatedLinksResponse
from app.schemas.stats import ClicksByDay, DeviceStats, StatsResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.dashboard import DashboardResponse, RecentLink


__all__ = ["URLCreate", "URLResponse", "PaginatedLinksResponse",
           "ClicksByDay", "DeviceStats", "StatsResponse",
           "UserCreate", "UserLogin", "UserResponse", "TokenResponse",
           "DashboardResponse", "RecentLink"]