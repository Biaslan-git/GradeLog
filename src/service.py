from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.models import User
from src.database import Session


@dataclass
class UserService:
    async_session: async_sessionmaker[AsyncSession] = Session

    async def add_user(
        self,
        chat_id: int, 
        username: str | None, 
        full_name: str, 
    ) -> User:
        user = User(
            chat_id=chat_id,
            username=username,
            full_name=full_name
        )
        async with self.async_session() as session:
            try:
                session.add(user)
                await session.commit()
                await session.refresh(user)
                return user
            except IntegrityError:
                await session.rollback()
                raise ValueError(f"User with chat_id {chat_id} already exists.")

    async def get_user(
        self,
        chat_id: int,
    ) -> User:
        q = select(User).where(User.chat_id == chat_id)
        async with self.async_session() as session:
            result = await session.execute(q)
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError('User does not exists')
            return user
