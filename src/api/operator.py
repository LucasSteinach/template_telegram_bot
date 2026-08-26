from fastapi import APIRouter, Depends

import src.application.usecases.support_chat_use_case as sc
import src.application.usecases.support_message_use_case as sm
import src.application.usecases.user_use_case as u
from src.api.response import IdMessage
from src.config import ROUTE
from src.dependencies.auth import get_auth_operator
from src.dependencies.usecases import (
    get_support_chat_use_case,
    get_support_message_use_case,
    get_user_use_case,
)

router = APIRouter(
    tags=["operator"],
)


@router.get(ROUTE.OPERATOR + "/profile", response_model=u.UserReadModel)
async def get_profile(
    user=Depends(get_auth_operator),
    uc: u.UserUseCase = Depends(get_user_use_case),
) -> u.UserReadModel:
    user = await uc.get_user(user.id)

    return u.user_read_model(user)


@router.get(ROUTE.OPERATOR + "/chats/{chat_id}")
async def get_chat(
    chat_id: int,
    _=Depends(get_auth_operator),
    uc: sc.SupportChatUseCase = Depends(get_support_chat_use_case),
) -> sc.SupportChatReadModel:
    chat = await uc.get_chat(chat_id)
    result = sc.support_chat_read_model(chat)

    return result


@router.post(ROUTE.OPERATOR + "/chats/{chat_id}")
async def send_answer(
    chat_id: int,
    req: sm.SendSupportMessage,
    operator=Depends(get_auth_operator),
    uc: sc.SupportChatUseCase = Depends(get_support_chat_use_case),
    messages_uc: sm.SupportMessageUseCase = Depends(get_support_message_use_case),
) -> IdMessage:
    chat = await uc.get_chat(chat_id)
    await uc.assign_operator(chat.id, operator.id, operator.role)
    message = await messages_uc.save_message(
        chat_id=chat.id, author_id=operator.id, author_role=operator.role, text=req.text
    )

    return IdMessage(detail="success", id=message.id)


@router.get(ROUTE.OPERATOR + "/chats/{chat_id}/history")
async def get_chat_history(
    chat_id: int,
    _=Depends(get_auth_operator),
    uc: sc.SupportChatUseCase = Depends(get_support_chat_use_case),
    messages_uc: sm.SupportMessageUseCase = Depends(get_support_message_use_case),
):
    chat = await uc.get_chat(chat_id)
    messages = await messages_uc.get_chat_history(chat.id)
    result = sm.chat_history(messages)

    return result


@router.get(ROUTE.OPERATOR + "/chats/assigned")
async def get_assigned_support_chats(
    operator=Depends(get_auth_operator),
    uc: sc.SupportChatUseCase = Depends(get_support_chat_use_case),
) -> list[sc.SupportChatReadModel]:
    chats = await uc.get_assigned_chats(operator.id)
    result = [sc.support_chat_read_model(chat) for chat in chats]

    return result


@router.get(ROUTE.OPERATOR + "/chats/waiting")
async def get_waiting_support_chats(
    operator=Depends(get_auth_operator),
    uc: sc.SupportChatUseCase = Depends(get_support_chat_use_case),
) -> list[sc.SupportChatReadModel]:
    chats = await uc.get_assigned_chats(operator.id)
    result = [sc.support_chat_read_model(chat) for chat in chats]

    return result
