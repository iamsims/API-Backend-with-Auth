import math
import time
from fastapi import APIRouter, Depends, HTTPException, status 

from urllib.parse import quote
from starlette.responses import JSONResponse
from fastapi import Request

from app.controllers.auth.api_key import generate_api_key
from app.controllers.auth.jwt_handler import set_cookie

from app.constants.exceptions import DATABASE_DOWN_EXCEPTION, DATABASE_EXCEPTION, DOESNT_EXIST_EXCEPTION, NOT_AUTHORIZED_EXCEPTION
from app.controllers.authenticate import get_current_user_id_http
from app.controllers.db import add_api_key, delete_api_key, get_api_keys, get_credit_for_user, get_credit_purchase_history, get_user_id_by_api_key

router = APIRouter()


@router.get("/ping")
async def ping():
    return {"result": True}


@router.get('/api-keys')
async def api_keys(request : Request, id_and_tokens:tuple = Depends(get_current_user_id_http)):
    id, access_token, refresh_token = id_and_tokens
    api_keys = await get_api_keys( id)
    api_keys = [dict(api_key) for api_key in api_keys]
    response = JSONResponse(content = api_keys, status_code=200)
    if access_token and refresh_token:
        set_cookie(response, access_token, refresh_token)

    return response
    

@router.delete('/api-key')
async def delete_api_keys(request : Request, api_key: str, id_and_tokens:tuple = Depends(get_current_user_id_http)):
    id, access_token, refresh_token = id_and_tokens
    id_api_key = await get_user_id_by_api_key( api_key)
    if id_api_key is None:
        raise DOESNT_EXIST_EXCEPTION("API key doesn't exist")
    
    if id_api_key != id:
        raise NOT_AUTHORIZED_EXCEPTION
    
    await delete_api_key( api_key)
    response = JSONResponse(content={"result": True}, status_code=200)
    if access_token and refresh_token:
        set_cookie(response, access_token, refresh_token)
    return response


@router.post("/api-keys/generate")
async def create_api_key( name : str = None, expiration_ts: int = None, id_and_tokens:tuple = Depends(get_current_user_id_http)):
    id, access_token, refresh_token = id_and_tokens
    api_key = generate_api_key()
    await add_api_key( id, api_key, name, expiration_ts)
    response = JSONResponse(content={"result": True, "api_key": api_key}, status_code=200)
    if access_token and refresh_token:
        set_cookie(response, access_token, refresh_token)
    return response
   
    


@router.get("/credit")
async def get_credit(request : Request, id_and_tokens:tuple = Depends(get_current_user_id_http)):
    id, access_token, refresh_token = id_and_tokens
    credit = await get_credit_for_user( id)
    response = JSONResponse(content=credit, status_code=200)
    if access_token and refresh_token:
        set_cookie(response, access_token, refresh_token)
    return response


@router.get("/credit/purchases")
async def get_credit_purchase(request:Request, id_and_tokens:tuple = Depends(get_current_user_id_http)):
    id, access_token, refresh_token = id_and_tokens
    history = await get_credit_purchase_history(id)
    response = JSONResponse(content=history, status_code=200)
    if access_token and refresh_token:
        set_cookie(response, access_token, refresh_token)
    return response
    