"""Helpers module for API"""
import hmac
import hashlib
import json
from os import getenv
import typing
from urllib.parse import parse_qsl

from fastapi import Header
from pydantic import BaseModel

import database as db

BOT_TOKEN = getenv("BOT_TOKEN")

class InitData(BaseModel):
    """Telegram web app init data model"""
    user_id: int
    can_send_messages: bool
    start: str

class APIException(Exception):
    """API internal class for custom exceptions"""
    def __init__(self, status_code: int = 400, error: str = "Bad Request"):
        self.error = error
        self.status_code = status_code

def validate_init_data(init_data: str) -> bool:
    """Validates the init data received from Telegram.

    Args:
        init_data (str): the init data received from Telegram

    Returns:
        bool: True if the init data is valid, False otherwise
    """
    secret = hmac.new(key=b"WebAppData", msg=BOT_TOKEN.encode(), digestmod=hashlib.sha256)

    try:
        parsed_data = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return False
    if "hash" not in parsed_data:
        return False
    hash_ = parsed_data.pop("hash")
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items(), key=lambda x: x[0])
    )
    sign = hmac.new(
        msg=data_check_string.encode(),
        key=secret.digest(),
        digestmod=hashlib.sha256
    ).hexdigest()
    return sign == hash_

def init_data_dependency(authorization: typing.Annotated[str, Header()]) -> InitData:
    """FastAPI dependency to validate the init data received from Telegram.

    Args:
        authorization (str): the init data received from Telegram
    Returns:
        InitData: Short InitData object
    """
    if not authorization.startswith("TGMA "):
        raise APIException(400, "INVALID_AUTHORIZATION_HEADER")
    init_data = authorization[5:]
    if not validate_init_data(init_data):
        raise APIException(403, "INVALID_INIT_DATA")
    parsed_data: dict[str, typing.Any] = dict(parse_qsl(init_data, strict_parsing=True))
    if parsed_data.get("user") is None:
        raise APIException(403, "NOT_A_USER")
    parsed_data["user"] = json.loads(parsed_data["user"])
    if not parsed_data["user"].get("allows_write_to_pm", False):
        raise APIException(
            400,
            "Разрешите боту отправлять сообщения /start (CANNOT_SEND_MESSAGES)"
        )
    if db.methods.users.get(int(parsed_data["user"]["id"])) is None and not db.methods.admins_ids.check_admin_access_by_id(parsed_data["user"]["id"]):
        raise APIException(
            status_code=404,
            error="Сначала нужно написать боту /start (USER_NOT_FOUND)"
        )
    return InitData(
        user_id=int(parsed_data["user"]["id"]),
        can_send_messages=parsed_data["user"]["allows_write_to_pm"],
        start=parsed_data.get("start_param", "")
    )

def service_auth_dependency(authorization: typing.Annotated[str, Header()]) -> None:
    """FastAPI dependency to validate the service token.

    Args:
        authorization (str): service token
    """
    if not authorization.startswith("Service "):
        raise APIException(400, "INVALID_AUTHORIZATION_HEADER")
    if authorization[8:] != getenv("SERVICE_API_TOKEN"):
        raise APIException(403, "INVALID_SERVICE_TOKEN")

T = typing.TypeVar('T')
class SuccessfulResponse(BaseModel, typing.Generic[T]):
    """Generic successful response model"""
    ok: bool = True
    response: T
