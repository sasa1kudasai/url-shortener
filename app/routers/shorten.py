from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy import select, func as sqlfunc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from app.cache import redis_client
from app.database import async_session, get_db

from app.schemas import URLResponse, URLCreate, StatsResponse, ClicksByDay, DeviceStats
from app.utils import encode_id, classify_device

from app.models import URL, Click, User
from app.auth import get_optional_user
router = APIRouter(tags=["shorten"])


async def log_click(code: str, user_agent: str | None, ip_address: str | None):
    async with async_session() as session:
        result = await session.execute(select(URL).where(URL.short_code == code))
        url_obj = result.scalar_one_or_none()
        if url_obj:
            url_obj.click_count += 1
            new_click = Click(url_id=url_obj.id, user_agent=user_agent, ip_address=ip_address)
            session.add(new_click)
            await session.commit()
    await redis_client.incr(f"clicks:{code}")


@router.post("/shorten", response_model=URLResponse)
async def shorten_url(data: URLCreate, db: AsyncSession = Depends(get_db), current_user: User | None = Depends(get_optional_user)):
    long_url_str = str(data.long_url)
    owner_id = current_user.id if current_user else None

    result = await db.execute(
        select(URL).where(URL.long_url == long_url_str, URL.owner_id == owner_id)
    )
    existing_url = result.scalar_one_or_none()
    if existing_url:
        return existing_url

    new_url = URL(short_code=None, long_url=long_url_str, owner_id=owner_id)
    db.add(new_url)
    await db.commit()
    await db.refresh(new_url)

    new_url.short_code = encode_id(new_url.id)
    await db.commit()
    await db.refresh(new_url)

    return new_url


@router.get("/{code}/stats", response_model=StatsResponse)
async def get_stats(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(URL).where(URL.short_code == code))
    url_obj = result.scalar_one_or_none()
    if url_obj is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    daily_result = await db.execute(
        select(
            sqlfunc.date(Click.clicked_at).label("day"),
            sqlfunc.count(Click.id).label("count"),
        )
        .where(Click.url_id == url_obj.id)
        .group_by(sqlfunc.date(Click.clicked_at))
        .order_by(sqlfunc.date(Click.clicked_at))
    )
    clicks_by_day = [ClicksByDay(day=row.day, count=row.count) for row in daily_result.all()]

    all_clicks_result = await db.execute(select(Click.user_agent).where(Click.url_id == url_obj.id))
    user_agents = all_clicks_result.scalars().all()

    device_counts: dict[str, int] = {}
    for ua_string in user_agents:
        device_type = classify_device(ua_string)
        device_counts[device_type] = device_counts.get(device_type, 0) + 1

    clicks_by_device = [DeviceStats(device_type=d, count=c) for d, c in device_counts.items()]

    return StatsResponse(
        short_code=url_obj.short_code,
        long_url=url_obj.long_url,
        total_clicks=url_obj.click_count,
        clicks_by_day=clicks_by_day,
        clicks_by_device=clicks_by_device,
    )


@router.get("/{code}")
async def redirect_to_url(code: str, request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None

    cached_url = await redis_client.get(code)
    if cached_url:
        background_tasks.add_task(log_click, code, user_agent, ip_address)
        return RedirectResponse(url=cached_url)

    result = await db.execute(select(URL).where(URL.short_code == code))
    url_obj = result.scalar_one_or_none()
    if url_obj is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    await redis_client.set(code, url_obj.long_url, ex=3600)
    background_tasks.add_task(log_click, code, user_agent, ip_address)

    return RedirectResponse(url=url_obj.long_url)