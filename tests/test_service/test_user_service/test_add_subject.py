import pytest
import pytest_asyncio

from src.service import UserService

@pytest.mark.asyncio
async def test_add_subject(user_service: UserService, default_user):
    new_subject = await user_service.add_subject(
        chat_id=default_user.chat_id,
        title='Test Subject',
        numerator=1,
        denominator=2
    )
    
    assert new_subject.user_id == default_user.id
    assert new_subject.title == 'Test Subject'
    assert new_subject.numerator == 1
    assert new_subject.denominator == 2

    with pytest.raises(ValueError):
        await user_service.add_subject(
            chat_id=000,
            title='Test Subject',
            numerator=1,
            denominator=2
        )

@pytest.mark.asyncio
async def test_add_subject_unique_constraints(user_service: UserService, default_user):
    await user_service.add_subject(
        chat_id=default_user.chat_id,
        title='Test Subject',
        numerator=1,
        denominator=2
    )

    with pytest.raises(ValueError):
        await user_service.add_subject(
            chat_id=default_user.chat_id,
            title='Test Subject',
            numerator=3,
            denominator=1
        )


