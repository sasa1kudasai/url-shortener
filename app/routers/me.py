from datetime import datetime, UTC

from fastapi import APIRouter, Depends
from sqlalchemy import select, func as sqlfunc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import URL, User
from app.auth import get_current_user
from app.schemas import DashboardResponse

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    totals_result = await db.execute(
        select(
            sqlfunc.coalesce(sqlfunc.sum(URL.click_count), 0).label("total_clicks"),
            sqlfunc.count(URL.id).label("active_links"),
        ).where(URL.owner_id == current_user.id)
    )
    totals = totals_result.one()

    days_since_registration = max((datetime.now(UTC) - current_user.created_at).days, 1)
    avg_clicks_per_day = round(totals.total_clicks / days_since_registration, 1)

    recent_result = await db.execute(
        select(URL)
        .where(URL.owner_id == current_user.id)
        .order_by(URL.created_at.desc())
        .limit(5)
    )
    recent_links = recent_result.scalars().all()

    return DashboardResponse(
        total_clicks=totals.total_clicks,
        active_links=totals.active_links,
        avg_clicks_per_day=avg_clicks_per_day,
        recent_links=recent_links,
    )