from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from src.service import UserService
from src.middlewares import error_handler
from src.states import AddSubjectState


router = Router()

@router.message(Command('subjects'))
@error_handler
async def subjects(message: types.Message):
    user_service = UserService()
    subjects = await user_service.get_user_subjects(message.chat.id)
    
    if subjects:
        answer_text = (
            'Ваши предметы:\n'
        ) + '\n'.join([f'/s{x.id} {x.title} | {x.numerator}/{x.denominator}' for x in subjects])
    else:
        answer_text = (
            'У вас нет ни одного добавленного предмета, сделайте это с помощью команды /add_subject'
        )

    await message.answer(answer_text)


@router.message(StateFilter(None), Command('add_subject'))
@error_handler
async def add_subject(message: types.Message, state: FSMContext):
    answer_text = (
        'Для добавления нового предмета отправьте сообщение в формате:\n'
        '<Название предмета> <соотношение/часов>\n\n'
        'Примеры:\n'
        'Экономика 1/2\n'
        'Мат. анализ 2/3\n\n'
        'Можно добавить несколько предметов одним сообщение, написав их каждый с новой строки.'
    )
    await message.answer(answer_text)
    await state.set_state(AddSubjectState.subject_name_and_coef)

@router.message(AddSubjectState.subject_name_and_coef, F.text)
@error_handler
async def add_subject_name_and_coef(message: types.Message, state: FSMContext):
    answer_on_error = (
        'Некорректный формат сообщения. Попробуйте еще раз.'
    )

    subjects = []
    try:
        for subject_text in message.text.split('\n'):
            title = subject_text[:-3] # type: ignore
            numerator, denominator = map(int, subject_text[-3:].split('/')) # type: ignore
            subjects.append([title, numerator, denominator])
    except ValueError:
        await message.answer(answer_on_error)
        return

    answer = ''
    user_service = UserService()
    for subject_data in subjects:
        subject = await user_service.add_subject(
            chat_id=message.chat.id,
            title=subject_data[0],
            numerator=subject_data[1],
            denominator=subject_data[2]
        )
        answer += f'- {subject.title} ({subject.numerator}/{subject.denominator})\n'

    if len(subjects) > 1:
        answer = 'Предметы добавлены:\n' + answer
    elif len(subjects) == 1:
        answer = 'Предмет добавлен:\n' + answer
    else:
        await message.answer(answer_on_error)
        return

    await message.answer(answer)
    await state.clear()
