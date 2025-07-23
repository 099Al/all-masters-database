from sqlalchemy import String, Float, Integer, Text, ForeignKey, Date, DateTime, Table, Column, \
    CheckConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import os
import enum
from sqlalchemy import Enum as SqlEnum

from src.database.models.base import Base

class UserStatus(enum.Enum):
    NEW = "new"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEW_CHANGES = "new_changes"
    BANNED = "ban"
    DELETED = "deleted"



class Specialist(Base):
    __tablename__ = 'specialists'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[UserStatus] = mapped_column(SqlEnum(UserStatus),default=UserStatus.NEW)  # new verified sent ban updated
    message_to_user: Mapped[str] = mapped_column(String(300), nullable=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=True)
    specialty: Mapped[str] = mapped_column(String(50), nullable=False)
    about: Mapped[str] = mapped_column(Text, nullable=False)
    photo_telegram: Mapped[str] = mapped_column(String(300), nullable=True)
    photo_local: Mapped[str] = mapped_column(String(300), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    ban_reason: Mapped[str] = mapped_column(String(300), nullable=True)


    def __repr__(self):
        return f"Specialist: {self.name} status: {self.status} created_at: {self.created_at}"







