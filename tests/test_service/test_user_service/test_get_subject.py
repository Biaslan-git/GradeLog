import pytest

from src.service import UserService

@pytest.mark.asyncio
async def test_get_subject(user_service: UserService, default_user):
    original_subject = await user_service.add_subject(
        chat_id=default_user.chat_id,
        title='Test Subject',
        numerator=1,
        denominator=2
    )

    getted_subject = await user_service.get_subject(chat_id=default_user.chat_id, subject_id=original_subject.id)

    assert getted_subject.id == original_subject.id
    assert getted_subject.user_id == original_subject.user_id
    assert getted_subject.title == original_subject.title
    assert getted_subject.numerator == original_subject.numerator
    assert getted_subject.denominator == original_subject.denominator

    with pytest.raises(ValueError):
        await user_service.get_subject(chat_id=000, subject_id=000)

    someone_user = await user_service.add_user(
        chat_id=000,
        username='testuser2',
        full_name='Test User 2'
    )
    someones_subject = await user_service.add_subject(
        chat_id=someone_user.chat_id,
        title='Someone elses Subject',
        numerator=1,
        denominator=2
    )

    with pytest.raises(ValueError):
        someone_elses_subject = await user_service.get_subject(
            chat_id=default_user.chat_id,
            subject_id=someones_subject.id
        )




