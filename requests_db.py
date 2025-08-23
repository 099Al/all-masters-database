from collections import defaultdict
from datetime import datetime, timedelta, timezone
from sqlite3 import IntegrityError

from sqlalchemy import select, func, text, or_

from src.config_paramaters import UTC_PLUS_5, SIMILARITY_THRESHOLD
from src.database.api_gpt import define_category_from_specialties
from src.database.connect import DataBase
from src.database.models import Specialist, ModerateData, ModerateLog, ModerateStatus, Category, Service
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

    async def get_specialist_data(self, user_id):
        async with self.session() as session:
            result = await session.execute(
                select(Specialist)
                .where(Specialist.id == user_id)
            )
            res = result.scalars().first()

        return res

    async def get_moderate_data(self, user_id):
        async with self.session() as session:
            result = await session.execute(
                select(ModerateData)
                .where(ModerateData.id == user_id)
            )
            res = result.scalars().first()

        return res

    async def get_moderate_specialist_info(self):
        async with self.session() as session:
            result = await session.execute(
                select(
                    ModerateData.id,
                    ModerateData.services,
                    ModerateData.about
                )
                .join(Specialist, Specialist.id == ModerateData.id)
                .where(
                    ModerateData.status.in_([ModerateStatus.NEW, ModerateStatus.NEW_CHANGES]),
                    or_(
                        ModerateData.applied_category == False,
                        ModerateData.applied_category == None
                    ),
                    or_(
                        ModerateData.services != Specialist.services,
                        ModerateData.about != Specialist.about
                    )
                )
            )
            res = result.all()

        return res


    async def update_specialist(self, user_id, **data):
        async with self.session() as session:
            await session.execute(
                update(Specialist)
                .where(Specialist.id == user_id)
                .values(**data)
            )
            await session.commit()

    async def update_moderate_data(self, user_id, **data):
        async with self.session() as session:
            await session.execute(
                update(ModerateData)
                .where(ModerateData.id == user_id)
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

    async def get_categories(self):
        async with self.session() as session:
            result = await session.execute(select(Category))
            res = result.scalars().all()
        return res

    async def get_services(self):
        async with self.session() as session:
            result = await session.execute(select(Service))
            res = result.scalars().all()
        return res


    async def get_category_services(self):
        async with self.session() as session:
            result = await session.execute(select(Category.name, Service.name).join(Service, Service.category_id == Category.id))
            res = result.all()

            category_services = defaultdict(list)
            for category, service in res:
                category_services[category].append(service)
            return dict(category_services)

    async def link_services_to_moderate(self, moderate_id: int, services_obj: list):
        async with self.session() as session:
            # Загружаем ModerateData
            moderate_obj = await session.get(ModerateData, moderate_id)

            if not moderate_obj:
                return None

            # Привязываем услуги
            for service in services_obj:
                if service not in moderate_obj.r_services:
                    moderate_obj.r_services.append(service)

            await session.commit()
            return moderate_obj




    async def call_update_statuses(self):
        async with self.session() as session:
            await session.execute(text("CALL update_statuses();"))
            await session.commit()





    # def _get_or_create_speciality(self, session, model, defaults=None, **kwargs):
    #     instance = session.execute(select(model).filter_by(**kwargs)).scalar_one_or_none()
    #     if instance:
    #         return instance
    #     params = {**kwargs, **(defaults or {})}
    #     instance = model(**params)
    #     session.add(instance)
    #     session.commit()
    #     return instance

    async def get_or_create_category(self,
            category_name: str,
            threshold: float = SIMILARITY_THRESHOLD
    ):
        """
        Ищет категорию по смысловой близости (similarity).
        Если не найдена — создаёт новую.
        threshold = 0.4 (можно регулировать, 0.3 слабое совпадение, 0.7 почти точное)
        """
        async with self.session() as session:  # type: AsyncSession
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
                # кто-то параллельно создал категорию → берём её из базы
                stmt = select(Category).where(Category.name == category_name)
                result = await session.execute(stmt)
                return result.scalar_one()

    async def get_or_create_service(
            self,
            service_name: str,
            category_id: int,
            threshold: float = SIMILARITY_THRESHOLD
    ):
        """
        Ищет услугу по смысловой близости (similarity) внутри категории.
        """
        async with self.session() as session:
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
                # кто-то параллельно создал услугу → берём её из базы
                stmt = select(Service).where(
                    Service.name == service_name,
                    Service.category_id == category_id
                )
                result = await session.execute(stmt)
                return result.scalar_one()

    async def get_or_create_services(self, service_names: list[str], category_id: int, threshold: float = SIMILARITY_THRESHOLD):
        """
        Массовая обработка списка услуг.
        Возвращает список объектов Service.
        """
        services = []
        async with self.session() as session:
            for name in service_names:
                # используем метод для каждой услуги
                service = await self.get_or_create_service(name, category_id, threshold)
                services.append(service)
            await session.commit()  # сохраняем все изменения
        return services

    #Метод работает по расписанию
    # CREATE EXTENSION IF NOT EXISTS pg_trgm;
    async def define_services(self):
        res = await self.get_moderate_specialist_info()

        info_categories = await self.get_categories()
        info_category_services = await self.get_category_services()

        for id, services_text, about in res:
            res = define_category_from_specialties(info_categories, info_category_services, services_text, about)
            category_name = res["category"]
            services_name = res["services"]
            work_types_name = res["work_types"]

            category_obj = await self.get_or_create_category(category_name)
            services_obj = await self.get_or_create_services(services_name, category_obj.id)

            await self.update_moderate_data(
                id,
                l_services=[service.name for service in services_obj],
                l_work_types=work_types_name,
                applied_category=True
            )

            await self.link_services_to_moderate(id, services_obj)










if __name__ == '__main__':
    import asyncio
    req = ReqData()
    res = asyncio.run(req.define_services())

    print(f" result: {res}")
    #print(res_work_types)



    #     for id, specialties in res:
    #         # TODO: возможно это делать вручную без api-gpt
    #         category_name = define_category_from_specialties(specialities, about, categories_list)
    #         category = self._get_or_create_speciality(session, Category, name=category_name)
    #         await self.update_moderate_data(id, category_id=category.id, applied_category=True)
    #
    #
    #
    #         for sp in specialties:
    #             spec_obj = self._get_or_create_speciality(session, Specialty, name=sp, category_id=category.id)
    #             specialist.specialties.append(spec_obj)
    #
    #             # 4. Виды работ
    #         for wt in work_types:
    #             wt_obj = self._get_or_create_speciality(session, WorkType, name=wt, category_id=category.id)
    #             specialist.work_types.append(wt_obj)
    #
    #     await session.commit()


