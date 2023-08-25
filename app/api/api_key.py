import math
import time
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status 

from urllib.parse import quote
from starlette.responses import JSONResponse
from fastapi import Request

from decouple import config
from app.controllers.auth.api_key import generate_api_key
from app.controllers.auth.jwt_handler import set_cookie

from app.constants.exceptions import  CREDENTIALS_EXCEPTION, DATABASE_DOWN_EXCEPTION, DATABASE_EXCEPTION, DOESNT_EXIST_EXCEPTION, NOT_AUTHORIZED_EXCEPTION
from app.controllers.authenticate import get_current_user_id_http
from app.controllers.db import add_api_key, delete_api_key, get_api_keys, get_credit_for_user, get_credit_purchase_history, get_logs, get_user_id_by_api_key

router = APIRouter()


@router.get("/ping")
async def ping():
    return {"result": True}


@router.get('/api-keys')
async def api_keys(request : Request, id_and_tokens:tuple = Depends(get_current_user_id_http)):
    try:
        id, access_token, refresh_token = id_and_tokens
        api_keys = await get_api_keys( id)
        api_keys = [dict(api_key) for api_key in api_keys]
        response = JSONResponse(content = api_keys, status_code=200)
        if access_token and refresh_token:
            set_cookie(response, access_token, refresh_token)

        return response
    
    except DATABASE_EXCEPTION:
        raise DATABASE_EXCEPTION
   
    except DATABASE_DOWN_EXCEPTION:
      raise DATABASE_DOWN_EXCEPTION
       
    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in getting api keys"
        )

@router.delete('/api-key')
async def delete_api_keys(request : Request, api_key: str, id_and_tokens:tuple = Depends(get_current_user_id_http)):
    try:
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

    
    except DATABASE_EXCEPTION:
        raise DATABASE_EXCEPTION
   
    except DATABASE_DOWN_EXCEPTION:
      raise DATABASE_DOWN_EXCEPTION
    
    except DOESNT_EXIST_EXCEPTION as e:
        raise e
    
    except NOT_AUTHORIZED_EXCEPTION:
        raise NOT_AUTHORIZED_EXCEPTION
       
    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in deleting api key"
        )

@router.post("/api-keys/generate")
async def create_api_key( name : str = None, expiration_ts: int = None, id_and_tokens:tuple = Depends(get_current_user_id_http)):
    try:
        id, access_token, refresh_token = id_and_tokens
        api_key = generate_api_key()
        await add_api_key( id, api_key, name, expiration_ts)
        response = JSONResponse(content={"result": True, "api_key": api_key}, status_code=200)
        if access_token and refresh_token:
            set_cookie(response, access_token, refresh_token)

        return response
    
    except DATABASE_EXCEPTION:
        raise DATABASE_EXCEPTION

    except DATABASE_DOWN_EXCEPTION:
      raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in generating api key"
        )
    


@router.get("/credit")
async def get_credit(request : Request, id_and_tokens:tuple = Depends(get_current_user_id_http)):
    try:
        id, access_token, refresh_token = id_and_tokens
        credit = await get_credit_for_user( id)
        response = JSONResponse(content=credit, status_code=200)
        if access_token and refresh_token:
            set_cookie(response, access_token, refresh_token)
        return response
    
    except DATABASE_EXCEPTION :
        raise DATABASE_EXCEPTION
    
    except DATABASE_DOWN_EXCEPTION:
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in getting user credit"
        )


@router.get("/credit/usage")
async def get_credit_usage(request : Request, api_key : str = None, page: int = 1, page_size: int = 10, id_and_tokens:tuple = Depends(get_current_user_id_http)):
    try:
        id, access_token, refresh_token = id_and_tokens
        paginated_logs = await get_logs( id , api_key, page, page_size)
        paginated_logs["logs"] = [dict(log) for log in paginated_logs["logs"]]
        response = JSONResponse(content=paginated_logs, status_code=200)

        if access_token and refresh_token:
            set_cookie(response, access_token, refresh_token)

        return response
        
    
    except DATABASE_EXCEPTION :
        raise DATABASE_EXCEPTION
    
    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in getting user credit"
        )
    

@router.get("/credit/purchases")
async def get_credit_purchase(request:Request, id_and_tokens:tuple = Depends(get_current_user_id_http)):
    try:
        id, access_token, refresh_token = id_and_tokens
        history = await get_credit_purchase_history(id)
        response = JSONResponse(content=history, status_code=200)
        if access_token and refresh_token:
            set_cookie(response, access_token, refresh_token)

        return response
        
    
    except DATABASE_EXCEPTION:
        raise DATABASE_EXCEPTION
    
    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in getting user credit"
        )  

@router.get('/refresh-token')
async def refresh(request:Request, id_tokens: tuple = Depends(get_current_user_id_http)):
    try:
        _, access_token, refresh_token = id_tokens
        response = JSONResponse(content={"result": True}, status_code=200)
        if refresh_token and access_token:
            set_cookie(response, access_token, refresh_token)
            print("Refreshed token")
        else:
            print("Refresh not required")

        return response
    
    except DATABASE_EXCEPTION:
        raise DATABASE_EXCEPTION
    
    except DATABASE_DOWN_EXCEPTION:
      raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in refreshing token"
        )

