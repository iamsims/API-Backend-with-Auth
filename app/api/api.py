from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status 

from urllib.parse import quote
from starlette.responses import JSONResponse
from fastapi import Request

from decouple import config
from app.auth.api_key import generate_api_key

from app.constants.exceptions import  DATABASE_DOWN_EXCEPTION, DATABASE_EXCEPTION
from app.controllers.db import add_api_key,  get_api_keys, get_credit_for_user, get_logs
from app.api.users_api import get_current_user_id

router = APIRouter()



@router.get('/api-keys')
async def api_keys(request : Request, id:int = Depends(get_current_user_id)):
    engine = request.app.state.engine
    try:
        api_keys = await get_api_keys(engine, id)
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

@router.post("/api-keys/generate")
async def api_key(request: Request, id :int = Depends(get_current_user_id) ):
    engine = request.app.state.engine
    try:
        api_key = generate_api_key()
        await add_api_key(engine, id, api_key)
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
async def get_credit(request : Request, id: int = Depends(get_current_user_id)):
    engine = request.app.state.engine
    try:
        credit = await get_credit_for_user(engine, id)
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
async def get_credit_usage(request : Request, api_key : str = None, page: int = 1, page_size: int = 10, id: int = Depends(get_current_user_id)):
    engine = request.app.state.engine
    try:
        paginated_logs = await get_logs(engine, id , api_key, page, page_size)
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
    


