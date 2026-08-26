import logging
import secrets
import string
import time
import uuid
from typing import Annotated

import bcrypt
import jwt
from fastapi import HTTPException
from pydantic import BaseModel, BeforeValidator, EmailStr
from redis import RedisError
from starlette import status

from src.domain.entities.user import UserRole
from src.infrastructure.redis.storage import RedisStorage

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

EmailLowercaseStr = Annotated[EmailStr, BeforeValidator(lambda v: str(v).lower())]


class Login(BaseModel):
    email: EmailLowercaseStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


def create_tokens(
    id_: str,
    data: dict,
    secret: str,
    access_exp_sec: int = 900,
    refresh_exp_sec: int = 3600 * 24 * 7,
) -> tuple[str, str, int]:
    now = int(time.time())

    access_payload = data.copy()
    access_payload["id_"] = id_
    access_payload["type"] = "access"
    access_payload["exp"] = now + access_exp_sec
    access_token: str = jwt.encode(access_payload, secret, algorithm=ALGORITHM)

    refresh_payload = access_payload.copy()
    refresh_payload["type"] = "refresh"
    refresh_payload["exp"] = now + refresh_exp_sec
    refresh_token: str = jwt.encode(refresh_payload, secret, algorithm=ALGORITHM)

    return access_token, refresh_token, access_exp_sec


def decode(token: str, secret: str) -> dict | None:
    try:
        return jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return None


class AuthUser(BaseModel):
    id: int
    role: UserRole


class AuthService:
    def __init__(
        self,
        jwt_secret: str,
        access_exp_sec: int,
        refresh_exp_sec: int,
        redis: RedisStorage,
    ):
        self.jwt_secret = jwt_secret
        self.access_exp_sec = access_exp_sec
        self.refresh_exp_sec = refresh_exp_sec
        self.redis = redis

    def decode_access_token(self, token: str) -> AuthUser:
        data = decode(token, self.jwt_secret)
        if not data or data.get("type") != "access":
            raise ValueError("Invalid token type")

        return (
            AuthUser(
                id=int(data["id_"]),
                role=data["role"],
            )
            if data
            else None
        )

    def decode_refresh_token(self, token: str) -> AuthUser:
        data = decode(token, self.jwt_secret)

        if not data or data.get("type") != "refresh":
            raise ValueError("Invalid token type")

        return AuthUser(
            id=int(data["id_"]),
            role=data["role"],
        )

    async def new_session(self, user_id: int, role: str) -> tuple[str, str, int]:
        token_id = uuid.uuid4().hex

        kwargs = {
            "id_": str(user_id),
            "data": {
                "role": role,
                "jti": token_id,
            },
            "secret": self.jwt_secret,
        }

        if self.access_exp_sec:
            kwargs["access_exp_sec"] = self.access_exp_sec
        if self.refresh_exp_sec:
            kwargs["refresh_exp_sec"] = self.refresh_exp_sec

        access_token, refresh_token, access_expires_in = create_tokens(**kwargs)

        await self.redis.save_refresh_token(
            user_id=user_id, token_id=token_id, expire_sec=self.refresh_exp_sec
        )

        return access_token, refresh_token, access_expires_in

    async def refresh_session(self, refresh_token: str) -> tuple[str, str, int]:
        payload = decode(refresh_token, self.jwt_secret)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id = int(payload["id_"])
        token_id = payload.get("data", {}).get("jti") or payload.get("jti")
        role = payload.get("data", {}).get("role") or payload.get("role")

        if not token_id:
            raise ValueError("Missing token identifier (jti)")

        is_valid_session = await self.redis.check_refresh_token(user_id, token_id)
        if not is_valid_session:
            raise ValueError("Refresh token revoked or expired")

        await self.redis.delete_refresh_token(user_id, token_id)

        return await self.new_session(user_id=user_id, role=role)

    async def logout_session(self, refresh_token: str) -> None:
        try:
            payload = decode(refresh_token, self.jwt_secret)
            if not payload or payload.get("type") != "refresh":
                return

            user_id = int(payload["id_"])
            token_id = payload.get("data", {}).get("jti") or payload.get("jti")

            if token_id:
                await self.redis.delete_refresh_token(user_id, token_id)
        except RedisError as e:
            logger.warning("Failed to clean up session during logout: %s", str(e))

    @staticmethod
    def generate_password(length: int = 8) -> str:
        uppercase = secrets.choice(string.ascii_uppercase)
        lowercase = secrets.choice(string.ascii_lowercase)
        digit = secrets.choice(string.digits)

        special_chars = "!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~"
        all_valid_chars = string.ascii_letters + string.digits + special_chars

        remaining_length = max(0, length - 3)
        remaining_chars = "".join(
            secrets.choice(all_valid_chars) for _ in range(remaining_length)
        )

        result_list = list(uppercase + lowercase + digit + remaining_chars)

        secrets.SystemRandom().shuffle(result_list)

        return "".join(result_list)

    @staticmethod
    def hash_password(password: str) -> str:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)

        return hashed_password.decode("utf-8")

    @staticmethod
    def check_password(password: str, hashed_password: str) -> None:
        if not bcrypt.checkpw(
            password.encode("utf-8"), hashed_password.encode("utf-8")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="wrong password",
                headers={"WWW-Authenticate": "Bearer"},
            )
