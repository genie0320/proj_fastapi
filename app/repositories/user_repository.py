from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RoleEnum, User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_users(self, skip: int = 0, limit: int = 20) -> list[User]:
        result = await self.db.execute(select(User).offset(skip).limit(limit).order_by(User.id))
        return list(result.scalars().all())

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_role(self, user: User, role: RoleEnum) -> User:
        user.role = role
        return await self.update(user)

    async def delete_by_id(self, user_id: int) -> None:
        await self.db.execute(delete(User).where(User.id == user_id))
        await self.db.commit()

