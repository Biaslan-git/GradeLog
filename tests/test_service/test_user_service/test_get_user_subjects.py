import pytest
import pytest_asyncio

from src.service import UserService

@pytest.mark.asyncio
async def test_get_user_subjects(user_service: UserService, default_user):
    user_subjects = await user_service.get_user_subjects(default_user.chat_id)
    assert user_subjects == []



