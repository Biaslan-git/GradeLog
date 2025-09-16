import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.models import Base

# общий движок
TEST_ENGINE = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

# Таблицы для каждого модуля
@pytest_asyncio.fixture(scope="function", autouse=True)
async def create_tables_module():
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def test_session():
    return async_sessionmaker(TEST_ENGINE, expire_on_commit=False)

@pytest_asyncio.fixture
async def async_session(test_session):
    async with test_session() as s:
        yield s

