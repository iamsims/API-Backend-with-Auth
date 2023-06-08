from typing import Union
from fastapi import Cookie

from fastapi import Request
from app.auth.jwt_handler import  decodeJWT, create_access_token, create_refresh_token
from app.constants.exceptions import COOKIE_EXCEPTION, CREDENTIALS_EXCEPTION
from app.controllers.db import get_user_by_id, is_token_blacklisted


async def get_current_user_token(request:Request, access_token: Union[str, None] = Cookie(None), refresh_token: Union[str, None] = Cookie(None)):
    if not access_token or not refresh_token:
        raise COOKIE_EXCEPTION
    _ = await get_current_user_id(access_token, refresh_token, refresh_tokens_generate=False)
    return access_token, refresh_token




async def get_current_user_id(access_token: str, refresh_token: str , refresh_tokens_generate: bool = True):
    if not access_token and not refresh_token:
        raise COOKIE_EXCEPTION
    
    payload = None
    new_access_token = None
    new_refresh_token = None

    if access_token:    
        payload = decodeJWT(token=access_token)

    # if access token is invalid, check if refresh token is valid
    if payload is None:
        print("Access token is invalid")
        if await is_token_blacklisted(refresh_token):
            print("Token is blacklisted")
            raise CREDENTIALS_EXCEPTION

        refresh_token_payload = decodeJWT(token=refresh_token)
        if refresh_token_payload is None:
            print("Unable to extract payload")
            raise CREDENTIALS_EXCEPTION  

        id = refresh_token_payload.get("id", None)
        if id is None:
            print("id could not be extracted")
            raise CREDENTIALS_EXCEPTION

        user = await get_user_by_id(id)
        if user and refresh_tokens_generate:
            new_access_token = create_access_token(data = {"id": id})
            new_refresh_token = create_refresh_token(data = {"id": id})
            return id, new_access_token, new_refresh_token

        elif user and not refresh_tokens_generate:
            return id, new_access_token, new_refresh_token

    else:
        id = payload.get("id", None)
    
        if id is None:
            print("id could not be extracted")
            raise CREDENTIALS_EXCEPTION
    
        user = await get_user_by_id(id)
        if user:
            return id, new_access_token, new_refresh_token
    
    raise CREDENTIALS_EXCEPTION


async def get_current_user_id_ws( access_token: str, refresh_token: str):
    return await get_current_user_id(access_token, refresh_token, refresh_tokens_generate=False)


async def get_current_user_id_http(request: Request, access_token: Union[str, None] = Cookie(None), refresh_token: Union[str, None] = Cookie(None)):
    return await get_current_user_id(access_token, refresh_token)



