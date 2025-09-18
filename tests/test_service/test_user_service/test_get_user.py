import pytest
import pytest_asyncio

from src.service import UserService

@pytest.mark.asyncio
async def test_get_user(user_service: UserService, default_user):
    user = await user_service.get_user(chat_id=default_user.chat_id)

    assert user.id == default_user.id
    assert user.chat_id == default_user.chat_id
    assert user.username == default_user.username
    assert user.full_name == default_user.full_name

    with pytest.raises(ValueError):
        incorrect_user = await user_service.get_user(chat_id=000)


    


