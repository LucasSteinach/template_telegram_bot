from fastapi import Request

from src.application.usecases.operator_use_case import OperatorUseCase
from src.application.usecases.support_chat_use_case import SupportChatUseCase
from src.application.usecases.support_message_use_case import SupportMessageUseCase
from src.application.usecases.user_use_case import UserUseCase


def get_user_use_case(request: Request) -> UserUseCase:
    return request.app.state.container.user_uc()


def get_operator_use_case(request: Request) -> OperatorUseCase:
    return request.app.state.container.operator_uc()


def get_support_chat_use_case(request: Request) -> SupportChatUseCase:
    return request.app.state.container.support_chat_uc()


def get_support_message_use_case(request: Request) -> SupportMessageUseCase:
    return request.app.state.container.support_message_uc()
