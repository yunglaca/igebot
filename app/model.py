from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(), nullable=False)
    last_name: Mapped[str] = mapped_column(String(), nullable=True)

    # Связь с таблицей EgeScore
    scores: Mapped[list["EgeScore"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class EgeScore(Base):

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    subject: Mapped[str] = mapped_column(String(), nullable=False)
    score: Mapped[int] = mapped_column(Integer(), nullable=False)

    # Связь с таблицей User
    user: Mapped[User] = relationship(back_populates="scores")
