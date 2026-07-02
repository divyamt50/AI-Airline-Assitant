from database import Base
from datetime import datetime, timezone
from sqlalchemy import String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

class TicketPrices(Base):
    __tablename__ = "ticket_prices"

    id:Mapped[int] = mapped_column(primary_key=True)
    city_name:Mapped[str] = mapped_column(String(255), nullable=False)
    price:Mapped[int] = mapped_column(Integer, nullable=False)
    created_at:Mapped[datetime] = mapped_column(server_default=func.now(timezone.utc))