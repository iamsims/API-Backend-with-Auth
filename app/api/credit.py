import datetime
import secrets
from typing import Union
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status 

import httpx
from jose import JWTError
from urllib.parse import quote
from starlette.config import Config
from starlette.responses import JSONResponse
from fastapi import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuthError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from decouple import config
from app.api.users_api import get_current_user_id
from app.auth.api_key import generate_api_key


from app.constants.exceptions import ALREADY_REGISTERED_EXCEPTION, COOKIE_EXCEPTION, CREDENTIALS_EXCEPTION, CREDIT_NOT_ENOUGH_EXCEPTION, DATABASE_DOWN_EXCEPTION, DATABASE_EXCEPTION, ENDPOINT_DOES_NOT_EXIST_EXCEPTION, INCORRECT_PASSWORD_EXCEPTION, INCORRECT_USERNAME_EXCEPTION, KUBER_EXCEPTION, PROVIDER_EXCEPTION
# from app.constants.exceptions import ALREADY_REGISTERED_EXCEPTION, COOKIE_EXCEPTION, CREDENTIALS_EXCEPTION, DATABASE_EXCEPTION, GITHUB_OAUTH_EXCEPTION, GOOGLE_OAUTH_EXCEPTION, INCORRENT_PASSWORD_EXCEPTION, INCORRENT_USERNAME_EXCEPTION, KUBER_EXCEPTION, LOGIN_EXCEPTION, PROVIDER_EXCEPTION, SIGNUP_EXCEPTION, CustomException
# from app.constants.exceptions import PROVIDER_EXCEPTION, MyException
from app.auth.jwt_handler import create_access_token, decodeJWT, create_refresh_token
from datetime import timedelta
from app.auth.password_handler import get_password_hash, verify_password

from app.controllers.db import add_api_key, add_user, decrement_endpoint_credit_for_user, get_api_keys, get_logs, get_user_by_data, get_user_by_id, get_user_id_by_data, users_exists_by_data, add_blacklist_token, is_token_blacklisted, get_all_users, users_exists_by_id, get_credit_for_user, add_credit_for_user

from app.models.users import UserinDB, UserLoginSchema

from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from app.constants.token import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from app.models.db import KUBER_ENDPOINTS_COST
from app.auth.oauth import get_github_token, get_google_token, get_user_info_github, oauth, GITHUB_CLIENT_ID


router = APIRouter()

@router.get("/")
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


@router.get("/usage")
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
    

