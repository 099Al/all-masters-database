from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config import settings
from src.database.models import *

class DataBase:

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(DataBase, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self.connect = settings.connect_url
        self.async_engine = create_async_engine(self.connect, echo=False)
        self.session = async_sessionmaker(bind=self.async_engine, class_=AsyncSession) #, expire_on_commit=False,
        self._initialized = True

    def get_session(self):
        return self.session

    def get_engine(self):
        return self.async_engine

    async def create_db(self):
        async with self.async_engine.begin() as connect:
            await connect.run_sync(Base.metadata.create_all)

    async def get_table(self, table_name):
        async with self.session() as session:
            result = await session.execute(select(table_name))
        return result.scalars().all()