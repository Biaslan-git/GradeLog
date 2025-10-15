from dataclasses import dataclass
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from typing import Sequence

from src.models import Grade, Subject, User
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

    async def get_grade(self, grade_id: int) -> Grade:
        q = select(Grade).where(Grade.id == grade_id)
        async with self.async_session() as session:
            try:
                result = await session.execute(q)
                grade = result.scalar_one()
                return grade
            except ValueError:
                raise ValueError('Grade does not exists.')

    async def add_grade(
        self, 
        chat_id: int,
        subject_id: int,
        grade1: str,
        grade2: int,
    ) -> Grade:
        user = await self.get_user(chat_id=chat_id)
        grade = Grade(
            user_id=user.id,
            subject_id=subject_id,
            grade1=grade1,
            grade2=grade2
        )

        async with self.async_session() as session:
            session.add(grade)
            await session.commit()
            await session.refresh(grade)
            return grade

    async def get_subject_grades(
        self,
        chat_id: int,
        subject_id: int,
    ) -> Sequence[Grade]:
        user = await self.get_user(chat_id)

        q = select(Grade).where((Grade.subject_id == subject_id) & (Grade.user_id == user.id)).order_by(Grade.id.desc())
        async with self.async_session() as session:
            try:
                result = await session.execute(q)
                grades = result.scalars().all()
                return grades
            except NoResultFound:
                raise ValueError('User does not exists.')

    async def delete_grade(self, chat_id: int, grade_id: int) -> Grade:
        q = select(Grade).where(Grade.id == grade_id)
        async with self.async_session() as session:
            try:
                result = await session.execute(q)
                grade = result.scalar_one()
                if grade.user.chat_id != chat_id:
                    raise ValueError('You do not have permission to access this resource.')

                # Удаляем предмет
                await session.delete(grade)
                await session.commit()  # Сохраняем изменения в базе данных
                
                return grade  # Возвращаем удаленный объект
            except NoResultFound:
                raise ValueError('Grade does not exist.')
            except ValueError as e:
                raise ValueError(str(e))


