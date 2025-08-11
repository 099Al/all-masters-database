from sqlalchemy import (
    String, Float, Integer, Text, Date, DateTime, Boolean,
    ForeignKey,  Table, Column,
    CheckConstraint, Enum, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import os
import enum
from sqlalchemy import Enum as SqlEnum

from src.config_paramaters import UTC_PLUS_5
from src.database.models.base import Base

class UserStatus(enum.Enum):
    NEW = "new"
    ACTIVE = "active"
    BANNED = "banned"


class ModerateStatus(enum.Enum):
    NEW = "new"
    NEW_CHANGES = "new_changes"
    APPROVED = "approved"
    REJECTED = "rejected"
    BANNED = "banned"
    PERMANENTLY_BANNED = "permanently_banned"
    DELETED = "deleted"
    DELAY = "delay"

class Specialist(Base):
    __tablename__ = 'specialists'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[UserStatus] = mapped_column(SqlEnum(UserStatus), default=UserStatus.NEW)
    moderate_result: Mapped[ModerateStatus] = mapped_column(SqlEnum(ModerateStatus), nullable=True)
    message_to_user: Mapped[str] = mapped_column(String(300), nullable=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False,  default='на модерации')
    phone: Mapped[str] = mapped_column(String(15), nullable=False,  default='на модерации')
    telegram: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(50), nullable=True)
    services: Mapped[str] = mapped_column(String(100), nullable=False,  default='на модерации')
    about: Mapped[str] = mapped_column(Text, nullable=False, default='на модерации')
    photo_telegram: Mapped[str] = mapped_column(String(300), nullable=True)
    photo_local: Mapped[str] = mapped_column(String(300), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    ban_reason: Mapped[str] = mapped_column(String(300), nullable=True)
    #cagtegory_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)

    #category = relationship("Category", back_populates="specialists")
    # services = relationship(
    #     "Service",
    #     secondary="specialist_services",
    #     back_populates="specialists"
    # )
    # work_types = relationship(
    #     "WorkType",
    #     secondary="specialist_work_types",
    #     back_populates="specialists"
    # )

    def __repr__(self):
        return f"Specialist: {self.name} status: {self.status} created_at: {self.created_at}"


class ModerateData(Base):
    __tablename__ = 'moderate_data'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[ModerateStatus] = mapped_column(SqlEnum(ModerateStatus), default=ModerateStatus.NEW)
    applied_category: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    message_to_user: Mapped[str] = mapped_column(String(300), nullable=True)
    name: Mapped[str] = mapped_column(String(30), nullable=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=True)
    telegram: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(50), nullable=True)
    services: Mapped[str] = mapped_column(String(100), nullable=True)
    about: Mapped[str] = mapped_column(Text, nullable=True)
    photo_telegram: Mapped[str] = mapped_column(String(300), nullable=True)
    photo_local: Mapped[str] = mapped_column(String(300), nullable=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    ban_reason: Mapped[str] = mapped_column(String(300), nullable=True)
    message_to_admin: Mapped[str] = mapped_column(String(700), nullable=True)
    #cagtegory_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)


    def __repr__(self):
        return f"Moderate: {self.name} status: {self.status} updated_at: {self.updated_at}"



class ModerateLog(Base):
    __tablename__ = 'moderate_log'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, primary_key=True, nullable=False)


class HistoryUsers(Base):
    __tablename__ = 'history_users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    telegram: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(50), nullable=True)
    services: Mapped[str] = mapped_column(String(100), nullable=True)
    photo_telegram: Mapped[str] = mapped_column(String(300), nullable=True)
    photo_local: Mapped[str] = mapped_column(String(300), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)




# class Category(Base):
#     __tablename__ = "categories"
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
#
#     services = relationship("Service", back_populates="category", cascade="all, delete-orphan")
#     work_types = relationship("WorkType", back_populates="category", cascade="all, delete-orphan")
#     specialists = relationship("Specialist", back_populates="category", cascade="all, delete-orphan")
#
# class Service(Base):
#     __tablename__ = "services"
#     __table_args__ = (UniqueConstraint("name", "category_id"),)
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
#
#     category = relationship("Category", back_populates="services")
#     work_types = relationship("WorkType", back_populates="services")
#     specialists = relationship(
#         "Specialist",
#         secondary="specialist_services",
#         back_populates="services"
#     )
#
#
# class WorkType(Base):
#     __tablename__ = "work_types"
#     __table_args__ = (UniqueConstraint("name", "service_id"),)
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
#     service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
#
#
#     category = relationship("Category", back_populates="work_types")
#     services = relationship("Service", back_populates="work_types")
#     specialists = relationship(
#         "Specialist",
#         secondary="specialist_work_types",
#         back_populates="work_types"
#     )
#
# class SpecialistService(Base):
#     __tablename__ = "specialist_services"
#
#     specialist_id = Column(Integer, ForeignKey("specialists.id"), primary_key=True)
#     service_id = Column(Integer, ForeignKey("services.id"), primary_key=True)
#
#
# class SpecialistWorkType(Base):
#     __tablename__ = "specialist_work_types"
#
#     specialist_id = Column(Integer, ForeignKey("specialists.id"), primary_key=True)
#     work_type_id = Column(Integer, ForeignKey("work_types.id"), primary_key=True)



