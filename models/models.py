from sqlalchemy import String, Float, Integer, Text, ForeignKey, Date, DateTime, Table, Column, \
    CheckConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import os
import enum
from sqlalchemy import Enum as SqlEnum

from src.database.models.base import Base

class UserStatus(enum.Enum):
    NEW = "new"
    ACTIVE = "active"
    BANNED = "ban"

class UserMoerateResult(enum.Enum):
    NEW_CHANGES = "new"
    APPROVED = "approved"
    BANNED = "ban"
    DELETED = "deleted"
    REJECTED = "rejected"
    DELAY = "delay"


class ModerateStatus(enum.Enum):
    NEW = "new"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEW_CHANGES = "new_changes"
    BANNED = "ban"
    PERMANENTLY_BANNED = "permanently_banned"
    DELETED = "deleted"

class Specialist(Base):
    __tablename__ = 'specialists'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[UserStatus] = mapped_column(SqlEnum(UserStatus), default=UserStatus.NEW)
    moderate_result: Mapped[UserMoerateResult] = mapped_column(SqlEnum(UserMoerateResult), nullable=True)
    message_to_user: Mapped[str] = mapped_column(String(300), nullable=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False,  default='на модерации')
    phone: Mapped[str] = mapped_column(String(15), nullable=False,  default='на модерации')
    telegram: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(50), nullable=True)
    specialty: Mapped[str] = mapped_column(String(100), nullable=False,  default='на модерации')
    about: Mapped[str] = mapped_column(Text, nullable=False, default='на модерации')
    photo_telegram: Mapped[str] = mapped_column(String(300), nullable=True)
    photo_local: Mapped[str] = mapped_column(String(300), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    ban_reason: Mapped[str] = mapped_column(String(300), nullable=True)


    def __repr__(self):
        return f"Specialist: {self.name} status: {self.status} created_at: {self.created_at}"


class ModerateData(Base):
    __tablename__ = 'moderate_data'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[ModerateStatus] = mapped_column(SqlEnum(ModerateStatus), default=ModerateStatus.NEW)
    message_to_user: Mapped[str] = mapped_column(String(300), nullable=True)
    name: Mapped[str] = mapped_column(String(30), nullable=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=True)
    telegram: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(50), nullable=True)
    specialty: Mapped[str] = mapped_column(String(100), nullable=True)
    about: Mapped[str] = mapped_column(Text, nullable=True)
    photo_telegram: Mapped[str] = mapped_column(String(300), nullable=True)
    photo_local: Mapped[str] = mapped_column(String(300), nullable=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    ban_reason: Mapped[str] = mapped_column(String(300), nullable=True)
    message_to_admin: Mapped[str] = mapped_column(String(700), nullable=True)


    def __repr__(self):
        return f"Moderate: {self.name} status: {self.status} updated_at: {self.updated_at}"



class ModerateLog(Base):
    __tablename__ = 'moderate_log'

    id: Mapped[int] = mapped_column(primary_key=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, primary_key=True, nullable=False)

