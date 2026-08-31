from time import timezone

from sqlalchemy import Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_code: Mapped[str | None] = mapped_column(String(), index=True, nullable=True)
    long_url: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    click_count: Mapped[int] = mapped_column(Integer, default=0)



class Click(Base):
    __tablename__ = "clicks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url_id: Mapped[int] = mapped_column(Integer, ForeignKey("urls.id"))
    clicked_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_agent: Mapped[str | None] = mapped_column(String(), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(), nullable=True)