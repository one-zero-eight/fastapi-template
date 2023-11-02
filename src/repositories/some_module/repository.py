__all__ = ["SomeModuleRepository"]


from sqlalchemy import select, insert, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from src.repositories.some_module.abc import AbstractSomeModuleRepository
from src.schemas import ViewSomeScheme, CreateSomeScheme, UpdateSomeScheme
from src.storages.sqlalchemy import AbstractSQLAlchemyStorage
from src.storages.sqlalchemy.models import SomeModel

# get_options = (selectinload(Model.some_field_raising_greenlet), )
get_options: tuple[ExecutableOption, ...] = ()


class SomeModuleRepository(AbstractSomeModuleRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ----------------- CRUD ----------------- #

    async def create(self, data: CreateSomeScheme) -> ViewSomeScheme:
        async with self._create_session() as session:
            _insert_query = insert(SomeModel).returning(SomeModel)
            if get_options:
                _insert_query = _insert_query.options(*get_options)
            obj = await session.scalar(_insert_query, params=data.model_dump())
            await session.commit()
            return ViewSomeScheme.model_validate(obj)

    async def batch_create(self, data: list[CreateSomeScheme]) -> list[ViewSomeScheme]:
        async with self._create_session() as session:
            if not data:
                return []
            _insert_query = insert(SomeModel).returning(SomeModel)
            if get_options:
                _insert_query = _insert_query.options(*get_options)
            objs = await session.scalars(_insert_query, params=[obj.model_dump() for obj in data])
            await session.commit()
            return [ViewSomeScheme.model_validate(obj) for obj in objs]

    async def read(self, id: int) -> ViewSomeScheme:
        async with self._create_session() as session:
            q = select(SomeModel).where(SomeModel.id == id)
            if get_options:
                q = q.options(*get_options)
            obj = await session.scalar(q)

            if obj:
                return ViewSomeScheme.model_validate(obj)

    async def read_all(self) -> list[ViewSomeScheme]:
        async with self._create_session() as session:
            q = select(SomeModel)
            if get_options:
                q = q.options(*get_options)
            objs = await session.scalars(q)
            return [ViewSomeScheme.model_validate(obj) for obj in objs]

    async def batch_read(self, ids: list[int]) -> list[ViewSomeScheme]:
        async with self._create_session() as session:
            if not ids:
                return []

            q = select(SomeModel).where(
                or_(
                    *[SomeModel.id == id for id in ids],
                )
            )

            if get_options:
                q = q.options(*get_options)
            objs = await session.scalars(q)

            return [ViewSomeScheme.model_validate(obj) for obj in objs]

    async def update(self, id_: int, data: UpdateSomeScheme):
        async with self._create_session() as session:
            q = update(SomeModel).where(SomeModel.id == id_).values(**data.model_dump()).returning(SomeModel)

            if get_options:
                q = q.options(*get_options)

            obj = await session.scalar(q)
            await session.commit()

            if obj:
                return ViewSomeScheme.model_validate(obj)

    # ^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^ #
