from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import URL

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def root(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(URL).order_by(URL.click_count.desc()))
    all_urls = result.scalars().all()

    return templates.TemplateResponse(request, "index.html", {"urls": all_urls})