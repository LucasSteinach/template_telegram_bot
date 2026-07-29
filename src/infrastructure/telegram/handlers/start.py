from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.application.dto.user_dto import RegisterUser
from src.container import Container
from src.infrastructure.telegram.keyboards.inline_keyboard import (
    inline_kb,
    InlineButton,
)

router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message, container: Container) -> None:
    dto = RegisterUser(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name or message.from_user.username,
    )

    async with container.session_factory() as session:
        use_case = container.register_user_use_case(session)
        user = await use_case.execute(dto)

    await message.answer(
        f"Hi, {user.full_name}!",
        reply_markup=inline_kb(
            [
                InlineButton(text="Hi", callback_data="hi"),
                InlineButton(text="bye", row=3, callback_data="bye"),
            ],
            day="day",
        ),
    )
