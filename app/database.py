from datetime import datetime

from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.config import settings


DATABASE_URL = settings.DATABASE_URL()
# Асинхронный движок для работы с PostgreSQL
engine = create_async_engine(
    url=DATABASE_URL,
    echo=True,  # Лог запросов SQLAlchemy для отладки
)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():  # type: ignore
    async with async_session_maker() as session:
        yield session


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"
