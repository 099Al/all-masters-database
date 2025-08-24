from collections import defaultdict
from datetime import datetime, timedelta, timezone
from sqlite3 import IntegrityError

from sqlalchemy import select, func, text, or_
from sqlalchemy.orm import selectinload


from src.config_paramaters import UTC_PLUS_5, SIMILARITY_THRESHOLD
from src.database.api_gpt import define_category_from_specialties
from src.database.connect import DataBase
from src.database.models import Specialist, ModerateData, ModerateLog, ModerateStatus, Category, Service
from sqlalchemy import update

from src.database.requests_db import ReqData


class ServiceManager(ReqData):
    """
    1. Отрабатывает функция, которая ищет категорию и услуги из описания клиента define_services()
    2. Далее вручную просматриваем списка, по условию is_new = True
       если все услуги корректны, то ставим is_new = False
       Аналогично категории.
    3. Далее вызываем функцию call_update_statuses()
       Функция переносит одобренные анкеты
       Далее идет перенос проверенных категорий и услуг
       После этого удаляем данные из ModerateData
    """


    def __init__(self):
        super().__init__()
        #self.session = DataBase().get_session()


    async def call_update_statuses(self):
        async with self.session() as session:
            await session.execute(text("CALL update_statuses();"))
            await session.commit()



    async def get_or_create_category(self,
            session,
            category_name: str,
            threshold: float = SIMILARITY_THRESHOLD
    ):
        """
        Ищет категорию по смысловой близости (similarity).
        Если не найдена — создаёт новую.
        threshold = 0.4 (можно регулировать, 0.3 слабое совпадение, 0.7 почти точное)
        """
        stmt = (
            select(Category, func.similarity(Category.name, category_name).label("sm"))
            .order_by(func.similarity(Category.name, category_name).desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        category = result.first()

        if category and category.sm >= threshold:
            return category[0]  # Category объект

        # если не нашли — создаём новую категорию
        new_category = Category(name=category_name, is_new=True)
        session.add(new_category)
        try:
            await session.flush()  # фиксируем INSERT, получаем id
            return new_category
        except IntegrityError:
            await session.rollback()
            # кто-то параллельно создал категорию -> берём её из базы
            stmt = select(Category).where(Category.name == category_name)
            result = await session.execute(stmt)
            return result.scalar_one()


    async def get_or_create_service(
            self,
            session,
            service_name: str,
            category_id: int,
            threshold: float = SIMILARITY_THRESHOLD
    ):
        """
        Ищет услугу по смысловой близости (similarity) внутри категории.
        """
        stmt = (
            select(Service, func.similarity(Service.name, service_name).label("sm"))
            .where(Service.category_id == category_id)
            .order_by(func.similarity(Service.name, service_name).desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        service = result.first()

        if service and service.sm >= threshold:
            return service[0]  # возвращаем найденную услугу

        # если не нашли — создаём новую
        new_service = Service(name=service_name, category_id=category_id, is_new=True)
        session.add(new_service)

        try:
            await session.flush()  # зафиксировать INSERT, получить id
            return new_service
        except IntegrityError:
            await session.rollback()
            # кто-то параллельно создал услугу -> берём её из базы
            stmt = select(Service).where(
                Service.name == service_name,
                Service.category_id == category_id
            )
            result = await session.execute(stmt)
            return result.scalar_one()


    async def get_or_create_services(self,
                                     session,
                                     service_names: list[str],
                                     category_id: int,
                                     threshold: float = SIMILARITY_THRESHOLD
    ):
        """
        Массовая обработка списка услуг.
        Возвращает список объектов Service.
        """
        services = []
        for name in service_names:
            # используем метод для каждой услуги
            service = await self.get_or_create_service(session, name, category_id, threshold)
            services.append(service)
        return services



    async def link_services_to_moderate(self, session, moderate_id: int, services_obj: list):
        moderate_obj = await session.get(
            ModerateData,
            moderate_id,
            options=(selectinload(ModerateData.r_services),) # для дозагрузки связей
        )
        if not moderate_obj:
            return None

        # Привязываем услуги
        existing_ids = {s.id for s in moderate_obj.r_services}
        for service in services_obj:
            if service.id not in existing_ids:
                moderate_obj.r_services.append(service)
        return moderate_obj




    #Метод работает по расписанию
    # CREATE EXTENSION IF NOT EXISTS pg_trgm;
    async def define_services(self):
        l_specialists = await self.get_moderate_specialist_info()

        info_categories = await self.get_categories()
        info_category_services = await self.get_category_services()

        async with self.session() as session:

            for id, services_text, about in l_specialists:
                res = define_category_from_specialties(info_categories, info_category_services, services_text, about)
                category_name = ["category"]
                services_name = res["services"]
                work_types_name = res["work_types"]

                category_obj = await self.get_or_create_category(session, category_name)
                services_obj = await self.get_or_create_services(session, services_name, category_obj.id)

                await self.update_moderate_data(
                    id,
                    session,
                    l_services=[service.name for service in services_obj],
                    l_work_types=work_types_name,
                    applied_category=True
                )

                await self.link_services_to_moderate(session, id, services_obj)

            await session.commit()




if __name__ == '__main__':
    import asyncio
    req = ServiceManager()
    res = asyncio.run(req.define_services())

    print(f" result: {res}")
    #print(res_work_types)

