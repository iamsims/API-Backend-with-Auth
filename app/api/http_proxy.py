import datetime
import secrets
import asyncio
import time
from typing import Union
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status, WebSocket, WebSocketDisconnect

import httpx
from jose import JWTError
from urllib.parse import quote
from starlette.config import Config
from starlette.responses import JSONResponse
from fastapi import Request

from decouple import config
from app.api.users_api import get_current_user_id_http


from app.constants.exceptions import ALREADY_REGISTERED_EXCEPTION, COOKIE_EXCEPTION, CREDENTIALS_EXCEPTION, CREDIT_NOT_ENOUGH_EXCEPTION, DATABASE_DOWN_EXCEPTION, DATABASE_EXCEPTION, ENDPOINT_DOES_NOT_EXIST_EXCEPTION, INCORRECT_PASSWORD_EXCEPTION, INCORRECT_USERNAME_EXCEPTION, KUBER_EXCEPTION, PROVIDER_EXCEPTION
# from app.constants.exceptions import ALREADY_REGISTERED_EXCEPTION, COOKIE_EXCEPTION, CREDENTIALS_EXCEPTION, DATABASE_EXCEPTION, GITHUB_OAUTH_EXCEPTION, GOOGLE_OAUTH_EXCEPTION, INCORRENT_PASSWORD_EXCEPTION, INCORRENT_USERNAME_EXCEPTION, KUBER_EXCEPTION, LOGIN_EXCEPTION, PROVIDER_EXCEPTION, SIGNUP_EXCEPTION, CustomException
# from app.constants.exceptions import PROVIDER_EXCEPTION, MyException

from app.controllers.db import add_api_key, add_user, decrement_endpoint_credit_for_user, get_api_keys, get_logs, get_user_by_data, get_user_by_id, get_user_id_by_data, users_exists_by_data, add_blacklist_token, is_token_blacklisted, get_all_users, users_exists_by_id, get_credit_for_user, add_credit_for_user


from fastapi.responses import StreamingResponse, HTMLResponse
from starlette.background import BackgroundTask
from app.models.db import KUBER_ENDPOINTS_COST


KUBER_SERVER = config('KUBER_SERVER') or None
if KUBER_SERVER is None:
    raise BaseException('Missing env variables for kuber server')




router = APIRouter() 

@router.route('/{endpoint:path}', methods=['GET', 'POST'])
async def reverse_proxy(request: Request):
    engine = request.app.state.engine
    try:
        if request.cookies.get('access_token'):
            token = request.cookies.get('access_token')
        else:
            raise COOKIE_EXCEPTION
    
        id = await get_current_user_id_http(request, token)

        
        if (id):
            path = request.url.path
            try:
                cost = KUBER_ENDPOINTS_COST[path]
            except KeyError as e:
                print(e)
                raise ENDPOINT_DOES_NOT_EXIST_EXCEPTION

            if await get_credit_for_user(engine, id) < cost:
                raise CREDIT_NOT_ENOUGH_EXCEPTION
            
            await decrement_endpoint_credit_for_user(engine, id, cost)
               
            try:
                client = request.app.state.client
                url = httpx.URL(path=path, query=request.url.query.encode('utf-8'))
                req = client.build_request(
                    request.method, url, headers=request.headers.raw, content=request.stream()
                )
                r = await client.send(req, stream=True)
                return StreamingResponse(
                    r.aiter_raw(),
                    status_code=r.status_code,
                    headers=r.headers,
                    background=BackgroundTask(r.aclose)
                )
            
            
            except Exception as e:
                print(e)
                raise KUBER_EXCEPTION
    
        else:
            raise CREDENTIALS_EXCEPTION
        

    except COOKIE_EXCEPTION as e:
        print(e)
        raise COOKIE_EXCEPTION
    
    except CREDENTIALS_EXCEPTION as e:
        print(e)
        raise CREDENTIALS_EXCEPTION
    
    except KUBER_EXCEPTION as e:
        print(e)
        raise KUBER_EXCEPTION
    
    except ENDPOINT_DOES_NOT_EXIST_EXCEPTION as e:
        print(e)
        raise ENDPOINT_DOES_NOT_EXIST_EXCEPTION
    

    except CREDIT_NOT_ENOUGH_EXCEPTION as e:
        print(e)
        raise CREDIT_NOT_ENOUGH_EXCEPTION

    except DATABASE_EXCEPTION as e:
        print(e)
        raise DATABASE_EXCEPTION

    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in reverse proxy"
        )

    

    

