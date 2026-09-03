from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_code: Mapped[str | None] = mapped_column(String(), index=True, nullable=True)
    long_url: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    owner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)