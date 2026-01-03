from sqlalchemy import select, func
from src.database.connect import DataBase
from src.database.models import Specialist, UserStatus, SpecialistPhoto, UserMessage, SpecialistService


class ReqWeb:
    def __init__(self):
        self.session = DataBase().get_session()

    async def get_active_specialists_data(self, service_id: int):
        async with self.session() as session:
            result = await session.execute(
                select(
                    Specialist.id,
                    Specialist.name,
                    Specialist.is_available,
                    Specialist.telegram,
                    Specialist.whatsapp,
                    Specialist.instagram,
                    Specialist.phone,
                    Specialist.email,
                    Specialist.photo_name,
                    Specialist.photo_location,
                    Specialist.photo_telegram,
                    Specialist.services,
                    Specialist.about
                )
                .join(SpecialistService, SpecialistService.specialist_id == Specialist.id)
                .where(Specialist.status == UserStatus.ACTIVE)
                .where(SpecialistService.service_id == service_id)
            )
            res = result.all()

        return res

    async def get_photo(self, specialist_id, type):
        async with self.session() as session:
            result = await session.execute(
                select(
                    SpecialistPhoto.photo_name
                )
                .where(SpecialistPhoto.specialist_id == specialist_id)
                .where(SpecialistPhoto.photo_type == type)
            )
            res = result.scalars().all()

        return res

    async def get_cnt_messages(self, user_id, start_of_hour, end_of_hour):
        # считаем количество сообщений за текущий час
        async with self.session() as session:
            stmt = (
                select(func.count(UserMessage.id))
                .where(
                    UserMessage.user_id == user_id,
                    UserMessage.created_at >= start_of_hour,
                    UserMessage.created_at < end_of_hour,
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one()