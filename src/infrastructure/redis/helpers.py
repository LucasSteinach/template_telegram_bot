import hashlib
import json

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup


def generate_message_hash(
    message_text: str, reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup
) -> str:
    data = {
        "text": message_text,
        "keyboard": reply_markup.model_dump() if reply_markup else None,
    }

    raw = json.dumps(
        data,
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.md5(raw.encode()).hexdigest()
