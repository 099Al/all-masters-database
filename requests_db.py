from collections import defaultdict
from datetime import datetime, timedelta, timezone
from sqlite3 import IntegrityError

from sqlalchemy import select, func, text, or_, literal
from sqlalchemy.orm import selectinload


from src.config_paramaters import UTC_PLUS_5, SIMILARITY_THRESHOLD
from src.database.api_gpt import define_category_from_specialties
from src.database.connect import DataBase
from src.database.models import Specialist, ModerateData, ModerateLog, ModerateStatus, Category, Service, \
    SpecialistService, UserStatus
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

    async def update_moderate_data(self, user_id, session=None, **data):
        local_session = False
        if not session:
            local_session = True
            session = self.session()
        await session.execute(
            update(ModerateData)
            .where(ModerateData.id == user_id)
            .values(**data)
        )
        if local_session:
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

    async def get_categories(self, is_new=None):
        async with self.session() as session:

            if is_new is not None:
                result = await session.execute(select(Category).where(Category.is_new == is_new))
                res = result.scalars().all()
            else:
                result = await session.execute(select(Category))
                res = result.scalars().all()

            return res


    async def get_services(self):
        async with self.session() as session:
            result = await session.execute(select(Service))
            res = result.scalars().all()
        return res

    async def get_services_by_category(self, category_id, is_new=False):
        async with self.session() as session:
            result = await session.execute(
                select(Service)
                .where(Service.category_id == category_id)
                .where(Service.is_new == is_new)
            )
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

    async def get_specialists_by_service(self, service_id):
        async with self.session() as session:
            result = await session.execute(
                select(Specialist)
                .join(SpecialistService, SpecialistService.specialist_id == Specialist.id)
                .where(SpecialistService.service_id == service_id)
                .where(Specialist.status == UserStatus.ACTIVE)
            )
            res = result.scalars().all()
        return res

    async def find_specialists_by_similarity(
            self,
            search_term: str,
            threshold: float = SIMILARITY_THRESHOLD,
    ):
        """
        Ищет специалистов по схожести search_term с l_services и l_work_types.
        Возвращает список (Specialist, similarity), отсортированный по убыванию similarity.
        """
        async with self.session() as session:
            l_services_elem = func.jsonb_array_elements_text(Specialist.l_services).table_valued("value")
            l_work_types_elem = func.jsonb_array_elements_text(Specialist.l_work_types).table_valued("value")

            sm_services = func.max(func.similarity(l_services_elem.c.value, literal(search_term)))
            sm_work_types = func.max(func.similarity(l_work_types_elem.c.value, literal(search_term)))

            stmt = (
                select(Specialist)
                .join(l_services_elem, literal(True), isouter=True)
                .join(l_work_types_elem, literal(True), isouter=True)
                .group_by(Specialist.id)
                .having(func.greatest(sm_services, sm_work_types) >= threshold)
                .order_by(func.greatest(sm_services, sm_work_types).desc())
            )

            result = await session.execute(stmt)
            specialists = result.scalars().all()

            return specialists

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


