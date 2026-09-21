import uuid as ui

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    model: type

    @classmethod
    async def add(cls, connection: AsyncSession, **data):
        new_id = ui.uuid4()
        query = (
            insert(cls.model)
            .values(id=new_id, **data)
            .returning(*cls.model.__table__.columns)
        )
        result = await connection.execute(query)
        return result.mappings().one()

    @classmethod
    async def get(cls, connection: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await connection.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, connection: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await connection.execute(query)
        return result.scalars().all()

    @classmethod
    async def rem(cls, connection: AsyncSession, **filter_by) -> None:
        query = delete(cls.model).filter_by(**filter_by)
        await connection.execute(query)

    @classmethod
    async def count(cls, connection: AsyncSession, **filter_by) -> int:
        query = select(func.count()).select_from(cls.model).filter_by(**filter_by)
        result = await connection.execute(query)
        return result.scalar_one()

    @classmethod
    async def update(cls, connection: AsyncSession, id: ui.UUID, **data):
        query = (
            update(cls.model)
            .where(cls.model.id == id)
            .values(**data)
            .returning(*cls.model.__table__.columns)
        )
        result = await connection.execute(query)
        return result.mappings().one()
