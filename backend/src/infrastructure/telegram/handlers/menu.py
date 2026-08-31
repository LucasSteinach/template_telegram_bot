from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from src.container import Container
from src.domain.entities.support_message import SupportMessage
from src.infrastructure.telegram.callbacks import MenuCallback
from src.infrastructure.telegram.keyboards.inline_keyboard import build_keyboard
from src.infrastructure.telegram.menu.helpers import get_menu_item

router = Router(name="menu")


def history_to_text(history: list[SupportMessage]):
    texts = []
    for message in history:
        texts.append(
            f"{message.author_role.upper() if message.author_role != 'user' else 'YOU'}\n"
            f"{message.text}\n"
        )
    return "\n".join(texts)


async def render_menu(message: Message, item_id: str = "root"):
    item = get_menu_item(item_id)
    keyboard = build_keyboard(item)

    await message.edit_text(text=item.message_text, reply_markup=keyboard)


@router.callback_query(MenuCallback.filter(F.item_id == "history"))
async def support_history_handler(
    callback: CallbackQuery, callback_data: MenuCallback, container: Container
):
    support_chat_uc = container.support_chat_uc()
    support_messages_uc = container.support_message_uc()

    chats = await support_chat_uc.get_user_chats(callback.from_user.id)
    text = "No history"

    if len(chats) != 0:
        chat = chats[-1]
        history = await support_messages_uc.get_chat_history(chat.id)

        text = (
            f"{chat.created_at.strftime('%Y.%m.%d')}\n"
            f"{chat.topic}\n\n"
            f"{history_to_text(history)}"
        )

    await menu_handler(callback, callback_data)
    await callback.message.edit_text(
        text=text, reply_markup=build_keyboard(get_menu_item("history"))
    )


@router.callback_query(MenuCallback.filter())
async def menu_handler(
    callback: CallbackQuery,
    callback_data: MenuCallback,
):
    await callback.answer()
    await render_menu(
        callback.message,
        callback_data.item_id,
    )
