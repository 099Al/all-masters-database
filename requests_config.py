from sqlalchemy import select

from src.database.models import Config


from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker

class DataBaseSync:
    def __init__(self, db_url_async: str, db_url_sync: str):
        self.async_engine = create_async_engine(db_url_async, echo=False)
        self.sync_engine = create_engine(db_url_sync, echo=False)

    def get_async_session(self):
        return async_sessionmaker(bind=self.async_engine, class_=AsyncSession)

    def get_sync_session(self):
        return sessionmaker(bind=self.sync_engine, expire_on_commit=False)


from sqlalchemy import select

class ReqConf:
    def __init__(self):
        self.session = DataBaseSync(...).get_sync_session()  # sessionmaker (sync)

    def get_params(self):
        with self.session() as session:
            result = session.execute(select(Config))
            return result.scalars().all()

    def get_param_by_key(self, key):
        with self.session() as session:
            result = session.execute(
                select(Config.value).where(Config.key == key)
            )
            return result.scalar_one_or_none()

