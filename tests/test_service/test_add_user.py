import pytest
import pytest_asyncio

from src.service import UserService

@pytest_asyncio.fixture
async def user_service(test_session):
    return UserService(test_session)

@pytest.mark.asyncio
async def test_add_user(user_service):
    user1 = await user_service.add_user(
        chat_id=12345,
        username='testuser',
        full_name='Test User',
    )
    
    assert user1.chat_id == 12345
    assert user1.username == 'testuser'
    assert user1.full_name == 'Test User'

    user2 = await user_service.add_user(
        chat_id=123456,
        username=None,
        full_name='Test User'
    )
    
    assert user2.username == None


@pytest.mark.asyncio
async def test_add_user_unique_constraints(user_service):
    await user_service.add_user(
        chat_id=12345,
        username='testuser',
        full_name='Test User'
    )

    with pytest.raises(ValueError):
        await user_service.add_user(
            chat_id=12345,
            username='testuser2',
            full_name='Test User 2'
        )
        

