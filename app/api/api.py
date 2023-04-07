import math
import time
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status 

from urllib.parse import quote
from starlette.responses import JSONResponse
from fastapi import Request

from decouple import config
from app.auth.api_key import generate_api_key

from app.constants.exceptions import  CREDENTIALS_EXCEPTION, DATABASE_DOWN_EXCEPTION, DATABASE_EXCEPTION, DOESNT_EXIST_EXCEPTION, NOT_AUTHORIZED_EXCEPTION
from app.api.users_api import get_current_user_id_http
from app.controllers.db import add_api_key, add_log_entry, delete_api_key, get_api_keys, get_credit_for_user, get_logs, get_user_id_by_api_key

router = APIRouter()



@router.get('/api-keys')
async def api_keys(request : Request, id:int = Depends(get_current_user_id_http)):
    try:
        api_keys = await get_api_keys( id)
        return api_keys
    
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
async def delete_api_keys(request : Request, api_key: str, id:int = Depends(get_current_user_id_http)):
    try:
        id_api_key = await get_user_id_by_api_key( api_key)
        if id_api_key is None:
            raise DOESNT_EXIST_EXCEPTION("API key doesn't exist")
        
        if id_api_key != id:
            raise NOT_AUTHORIZED_EXCEPTION
        
        await delete_api_key( api_key)
        return JSONResponse(content={"result": True}, status_code=200)
    
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
async def api_key(request: Request, name : str = None, id :int = Depends(get_current_user_id_http)):
    try:
        api_key = generate_api_key()
        await add_api_key( id, api_key, name)
        return JSONResponse(content={"result": True, "api_key": api_key}, status_code=200)
    
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
async def get_credit(request : Request, id: int = Depends(get_current_user_id_http)):
    try:
        credit = await get_credit_for_user( id)
        return credit
    
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
async def get_credit_usage(request : Request, api_key : str = None, page: int = 1, page_size: int = 10, id: int = Depends(get_current_user_id_http)):
    try:
        paginated_logs = await get_logs( id , api_key, page, page_size)
        return paginated_logs
        
    
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
    


