from typing import Optional

from fastapi import Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette.requests import Request

from app.constants import app_constants


class Token(BaseModel):
    access_token: str
    refresh_token: str


async def get_token(request: Request, api_key: Optional[str] = Depends(
    APIKeyHeader(
        name=app_constants.authorization,
        auto_error=False))) -> Optional[str]:
    """
    Get the token from the request if authorization header
    is present otherwise get token from cookie
    """
    cookie = request.cookies.get(app_constants.authorization)
    return cookie
    # if api_key:
    #     scheme, _, token = api_key.partition(" ")
    #     return token if scheme.lower() == "bearer" else None
    # else:
    #     return request.cookies.get(app_constants.authorization)


async def get_refresh_token(request: Request, api_key: Optional[str] = Depends(
    APIKeyHeader(
        name=app_constants.refresh_token,
        auto_error=False))) -> Optional[str]:
    cookie = request.cookies.get(app_constants.refresh_token)
    return cookie


async def get_google_state(request: Request, api_key: Optional[str] = Depends(
    APIKeyHeader(
        name=app_constants.state,
        auto_error=False))) -> Optional[str]:
    cookie = request.cookies.get(app_constants.state)
    return cookie
