from sqlalchemy import select
from src.database.connect import DataBase
from src.database.models import Specialist, UserStatus, UserPhoto


class ReqWeb:
    def __init__(self):
        self.session = DataBase().get_session()

    async def get_active_specialists_data(self):
        async with self.session() as session:
            result = await session.execute(
                select(
                    Specialist.name,
                    Specialist.email,
                    Specialist.telegram,
                    Specialist.whatsapp,
                    Specialist.instagram,
                    Specialist.phone,
                    Specialist.photo_name,
                    Specialist.photo_location,
                    Specialist.photo_telegram,
                    Specialist.services,
                    Specialist.about
                )
                .where(Specialist.status == UserStatus.ACTIVE)
            )
            res = result.all()

        return res

    async def get_photo(self, user_id, type):
        async with self.session() as session:
            result = await session.execute(
                select(
                    UserPhoto.photo_name,
                    UserPhoto.user_id
                )
                .where(UserPhoto.id == user_id)
                .where(UserPhoto.photo_type == type)
            )
            res = result.all()

        return res