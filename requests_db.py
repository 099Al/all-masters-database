from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func

from src.config_paramaters import UTC_PLUS_5
from src.database.connect import DataBase
from src.database.models import Specialist, ModerateData, ModerateLog
from sqlalchemy import update




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

    async def update_specialist(self, user_id, **data):
        async with self.session() as session:
            await session.execute(
                update(Specialist)
                .where(Specialist.id == user_id)
                .values(**data)
            )
            await session.commit()

    async def get_cnt_edit_request(self, user_id):
        async with self.session() as session:
            result = await session.execute(
                select(func.count())
                .select_from(ModerateLog)
                .where(
                    ModerateLog.user_id == user_id,
                    ModerateLog.updated_at >= (datetime.now(UTC_PLUS_5) - timedelta(hours=1)).replace(tzinfo=None)
                )
            )
            count = result.scalar_one()

        return count