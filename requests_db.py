from sqlalchemy.future import select

from src.database.connect import DataBase
from src.database.models import Specialist, ModerateData


class ReqData:
    def __init__(self):
        self.session = DataBase().get_session()


    async def save_profile_data(self, user):
        async with self.session() as session:
            async with session.begin():
                session.add(user)

    async def merge_profile_data(self, user):
        async with self.session() as session:
            async with session.begin():
                await session.merge(user)

    async def get_specialist_date(self, user_id):
        async with self.session() as session:
            result = await session.execute(
                select(Specialist)
                .where(Specialist.id == user_id)
            )
            res = result.scalars().first()

        return res

    async def get_moderate_date(self, user_id):
        async with self.session() as session:
            result = await session.execute(
                select(ModerateData)
                .where(ModerateData.id == user_id)
            )
            res = result.scalars().first()

        return res