import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from src.models import User, Subject, Grade
from src.database import Base


# Тесты для модели User
@pytest.mark.asyncio
async def test_user_model(async_session):
    # Создаем пользователя
    user = User(chat_id=123456, username="testuser", full_name="Test User")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    # Проверяем, что пользователь был создан
    assert user.id is not None
    assert user.chat_id == 123456
    assert user.username == "testuser"
    assert user.full_name == "Test User"
    
    # Явно загружаем отношения
    stmt = select(User).options(selectinload(User.subjects), selectinload(User.grades)).where(User.id == user.id)
    result = await async_session.execute(stmt)
    user_with_relations = result.scalar_one()
    
    # Проверяем, что отношения инициализированы
    assert user_with_relations.subjects == []
    assert user_with_relations.grades == []

# Тесты для модели Subject
@pytest.mark.asyncio
async def test_subject_model(async_session):
    # Создаем пользователя
    user = User(chat_id=123456, username="testuser", full_name="Test User")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    # Создаем предмет
    subject = Subject(title="Math", numerator=5, denominator=10, user_id=user.id)
    async_session.add(subject)
    await async_session.commit()
    await async_session.refresh(subject)
    
    # Проверяем, что предмет был создан
    assert subject.id is not None
    assert subject.title == "Math"
    assert subject.numerator == 5
    assert subject.denominator == 10
    assert subject.user_id == user.id
    
    # Явно загружаем отношения
    stmt = select(Subject).options(selectinload(Subject.grades)).where(Subject.id == subject.id)
    result = await async_session.execute(stmt)
    subject_with_relations = result.scalar_one()
    
    # Проверяем, что отношения инициализированы
    assert subject_with_relations.grades == []

# Тесты для модели Grade
@pytest.mark.asyncio
async def test_grade_model(async_session):
    # Создаем пользователя
    user = User(chat_id=123456, username="testuser", full_name="Test User")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    # Создаем предмет
    subject = Subject(title="Math", numerator=5, denominator=10, user_id=user.id)
    async_session.add(subject)
    await async_session.commit()
    await async_session.refresh(subject)
    
    # Создаем оценку
    grade = Grade(grade1=4, grade2=5, user_id=user.id, subject_id=subject.id)
    async_session.add(grade)
    await async_session.commit()
    await async_session.refresh(grade)
    
    # Проверяем, что оценка была создана
    assert grade.id is not None
    assert grade.grade1 == 4
    assert grade.grade2 == 5
    assert grade.user_id == user.id
    assert grade.subject_id == subject.id

# Тесты для уникальности полей пользователя
@pytest.mark.asyncio
async def test_user_unique_constraints(async_session):
    # Создаем первого пользователя
    user1 = User(chat_id=123456, username="testuser1", full_name="Test User 1")
    async_session.add(user1)
    await async_session.commit()
    
    # Пытаемся создать второго пользователя с тем же chat_id
    user2 = User(chat_id=123456, username="testuser2", full_name="Test User 2")
    async_session.add(user2)
    
    # Ожидаем ошибку IntegrityError
    with pytest.raises(IntegrityError):
        await async_session.commit()
    
    # Откатываем транзакцию
    await async_session.rollback()
   

# Тесты для каскадного удаления
@pytest.mark.asyncio
async def test_cascade_delete(async_session):
    # Создаем пользователя
    user = User(chat_id=123456, username="testuser3", full_name="Test User")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    # Создаем предмет
    subject = Subject(title="Math", numerator=5, denominator=10, user_id=user.id)
    async_session.add(subject)
    await async_session.commit()
    await async_session.refresh(subject)
    
    # Создаем оценку
    grade = Grade(grade1=4, grade2=5, user_id=user.id, subject_id=subject.id)
    async_session.add(grade)
    await async_session.commit()
    await async_session.refresh(grade)
    
    # Удаляем пользователя
    await async_session.delete(user)
    await async_session.commit()
    
    # Проверяем, что предмет и оценка также были удалены
    stmt = select(Subject).where(Subject.id == subject.id)
    result = await async_session.execute(stmt)
    deleted_subject = result.scalar_one_or_none()
    assert deleted_subject is None
    
    stmt = select(Grade).where(Grade.id == grade.id)
    result = await async_session.execute(stmt)
    deleted_grade = result.scalar_one_or_none()
    assert deleted_grade is None

# Тесты для отношений
@pytest.mark.asyncio
async def test_user_subjects_relationship(async_session):
    # Создаем пользователя
    user = User(chat_id=123456, username="testuser4", full_name="Test User")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    # Создаем предметы
    subject1 = Subject(title="Math", numerator=5, denominator=10, user_id=user.id)
    subject2 = Subject(title="Science", numerator=4, denominator=8, user_id=user.id)
    async_session.add_all([subject1, subject2])
    await async_session.commit()
    await async_session.refresh(subject1)
    await async_session.refresh(subject2)
    
    # Явно загружаем отношения
    stmt = select(User).options(selectinload(User.subjects)).where(User.id == user.id)
    result = await async_session.execute(stmt)
    user_with_subjects = result.scalar_one()
    
    # Проверяем, что предметы доступны через отношение
    assert len(user_with_subjects.subjects) == 2
    assert subject1 in user_with_subjects.subjects
    assert subject2 in user_with_subjects.subjects

@pytest.mark.asyncio
async def test_subject_grades_relationship(async_session):
    # Создаем пользователя
    user = User(chat_id=123456, username="testuser", full_name="Test User")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    # Создаем предмет
    subject = Subject(title="Math", numerator=5, denominator=10, user_id=user.id)
    async_session.add(subject)
    await async_session.commit()
    await async_session.refresh(subject)
    
    # Создаем оценки
    grade1 = Grade(grade1=4, grade2=5, user_id=user.id, subject_id=subject.id)
    grade2 = Grade(grade1=3, grade2=4, user_id=user.id, subject_id=subject.id)
    async_session.add_all([grade1, grade2])
    await async_session.commit()
    await async_session.refresh(grade1)
    await async_session.refresh(grade2)
    
    # Явно загружаем отношения
    stmt = select(Subject).options(selectinload(Subject.grades)).where(Subject.id == subject.id)
    result = await async_session.execute(stmt)
    subject_with_grades = result.scalar_one()
    
    # Проверяем, что оценки доступны через отношение
    assert len(subject_with_grades.grades) == 2
    assert grade1 in subject_with_grades.grades
    assert grade2 in subject_with_grades.grades

