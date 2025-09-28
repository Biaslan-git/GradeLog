from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.models import Subject, User
from src.database import Session


@dataclass
class UserService:
    async_session: async_sessionmaker[AsyncSession] = Session

    async def add_user(self, chat_id: int, username: str | None, full_name: str) -> User:
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

    async def get_user(self, chat_id: int) -> User:
        q = select(User).where(User.chat_id == chat_id)
        async with self.async_session() as session:
            try:
                result = await session.execute(q)
                user = result.scalar_one()
                return user
            except NoResultFound:
                raise ValueError('User does not exists.')

    async def get_user_subjects(self, chat_id: int) -> list[Subject]:
        q = select(User).where(User.chat_id == chat_id)
        async with self.async_session() as session:
            try:
                result = await session.execute(q)
                user = result.scalar_one()
                return list(user.subjects)
            except NoResultFound:
                raise ValueError('User does not exists.')

    async def get_subject(self, chat_id: int, subject_id: int) -> Subject:
        q = select(Subject).where(Subject.id == subject_id)
        async with self.async_session() as session:
            try:
                result = await session.execute(q)
                subject = result.scalar_one()
                if subject.user.chat_id != chat_id:
                    raise ValueError
                return subject
            except NoResultFound:
                raise ValueError('User does not exists.')
            except ValueError:
                raise ValueError('You do not have permission to access this resource')

    async def add_subject(
        self, 
        chat_id: int,
        title: str,
        numerator: int,
        denominator: int,
    ) -> Subject:
        user = await self.get_user(chat_id=chat_id)
        subject = Subject(
            user_id=user.id,
            title=title,
            numerator=numerator,
            denominator=denominator
        )

        async with self.async_session() as session:
            try:
                session.add(subject)
                await session.commit()
                await session.refresh(subject)
            except IntegrityError:
                await session.rollback()
                raise ValueError('This subject title already exists in this user subjects/')
            return subject

    async def delete_subject(self, chat_id: int, subject_id: int) -> Subject:
        q = select(Subject).where(Subject.id == subject_id)
        async with self.async_session() as session:
            try:
                result = await session.execute(q)
                subject = result.scalar_one()
                if subject.user.chat_id != chat_id:
                    raise ValueError('You do not have permission to access this resource.')

                # Удаляем предмет
                await session.delete(subject)
                await session.commit()  # Сохраняем изменения в базе данных
                
                return subject  # Возвращаем удаленный объект
            except NoResultFound:
                raise ValueError('Subject does not exist.')
            except ValueError as e:
                raise ValueError(str(e))

