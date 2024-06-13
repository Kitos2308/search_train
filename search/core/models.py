import uuid
from sqlalchemy import String, DateTime, Boolean, Date
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

    pass
