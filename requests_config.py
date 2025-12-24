from collections import defaultdict
from datetime import datetime, timedelta
from sqlalchemy import select
from src.database.connect import DataBase
from src.database.models import Config


class ReqConf:
    def __init__(self):
        self.session = DataBase().get_session()


    async def get_params(self):
        async with self.session() as session:
            result = await session.execute(select(Config))
            res = result.scalars().all()
        return res

    async def get_param_by_key(self, key):
        async with self.session() as session:
            result = await session.execute(
                select(Config.value)
                .where(Config.key == key)
            )
            res = result.scalars().all()
        return res
