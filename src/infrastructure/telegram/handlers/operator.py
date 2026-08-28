from aiogram import Bot, Dispatcher

from src.infrastructure.telegram.handlers.actions.helpers import add_messages_to_cleanup


async def handle_support_message(
    bot: Bot,
    dispatcher: Dispatcher,
    chat_id: int,
    text: str,
) -> None:
    message = await bot.send_message(
        chat_id=chat_id,
        text=text,
    )
    state = dispatcher.fsm.get_context(
        bot=bot,
        chat_id=chat_id,
        user_id=chat_id,
    )

    await add_messages_to_cleanup(
        state,
        [message.message_id],
    )
