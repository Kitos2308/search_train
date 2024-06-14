import uuid
from sqlalchemy import String, DateTime, Boolean, Date, INTEGER
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.sql import expression
from datetime import datetime, date
import uuid

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from search.settings import settings

base_metadata = MetaData(
    schema=settings.DB_SCHEMA
)


class Base(DeclarativeBase):
    metadata = base_metadata


class ExampleText(Base):
    __tablename__ = "text_one"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, default=uuid.uuid4, index=True, unique=True)
    type: Mapped[str] = mapped_column(String)
    source_txt1: Mapped[str] = mapped_column(String, )
    source_txt2: Mapped[str] = mapped_column(String, )
    source_txt3: Mapped[str] = mapped_column(String, )
    source_txt4: Mapped[str] = mapped_column(String, )
    img: Mapped[str] = mapped_column(String,)
    entity_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)


