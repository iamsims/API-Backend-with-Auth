from typing import Union
from fastapi import Cookie

from fastapi import Request
from app.auth.jwt_handler import  decodeJWT
from app.constants.exceptions import COOKIE_EXCEPTION, CREDENTIALS_EXCEPTION
from app.controllers.db import get_user_by_id, is_token_blacklisted




async def get_current_user_token(request:Request, access_token: Union[str, None] = Cookie(None)):
    if access_token is None:
        raise COOKIE_EXCEPTION
    _ = await get_current_user_id_http(request, access_token)
    return access_token


async def get_current_user_id_ws( access_token: str):
    if access_token is None:
        raise COOKIE_EXCEPTION

    if await is_token_blacklisted( access_token):
        print("Token is blacklisted")
        raise CREDENTIALS_EXCEPTION
        
    payload = decodeJWT(token=access_token)

    if payload is None:
        print("Unable to extract payload")
        raise CREDENTIALS_EXCEPTION
   
    
    id = payload.get("id", None)
    
    if id is None:
        print("id could not be extracted")
        raise CREDENTIALS_EXCEPTION
    
    user = await get_user_by_id(id)
    if user:
        return id 
    
    raise CREDENTIALS_EXCEPTION



async def get_current_user_id_http(request: Request, access_token: Union[str, None] = Cookie(None)):
    if access_token is None:
        raise COOKIE_EXCEPTION

    if await is_token_blacklisted(access_token):
        print("Token is blacklisted")
        raise CREDENTIALS_EXCEPTION
    
    payload = decodeJWT(token=access_token)
    
    if payload is None:
        print("Unable to extract payload")
        raise CREDENTIALS_EXCEPTION
    
    id = payload.get("id", None)
    
    if id is None:
        print("id could not be extracted")
        raise CREDENTIALS_EXCEPTION
    
    user = await get_user_by_id(id)
    if user:
        return id 
    
    raise CREDENTIALS_EXCEPTION
