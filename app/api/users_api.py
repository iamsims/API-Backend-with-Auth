import datetime
import secrets
import traceback
from typing import Union
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, WebSocket, status 

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
from urllib.parse import *

@router.get('/sso/login/{provider}')
async def login(provider: str, request: Request, state : str = None,redirect_url: str=None):
    try:
        match provider:
            case "google":
                
                base_url = request.base_url
                referer=request.headers.get('referer')
                
                client_redirect_url=redirect_uri=request.query_params.get('redirect_url')
                if client_redirect_url:
                    redirect_uri=client_redirect_url
                elif referer: 
                    referer_url = urlparse(referer,"")
                    redirect_uri=referer_url.scheme+"://"+referer_url.netloc+"/kuber/oauth/callback/google"
                else:
                    redirect_uri = f"{base_url}auth/sso/callback/google"
                    
                return await oauth.google.authorize_redirect(request, redirect_uri, state = state)
    
            case "github":
                scope = "read:user user:email"
                encoded_scope = quote(scope)
                return RedirectResponse(url = f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope={encoded_scope}&state={state}', status_code = 302) 
                
            case _:
                raise PROVIDER_EXCEPTION
            
    except PROVIDER_EXCEPTION:
        raise PROVIDER_EXCEPTION
    

    except Exception as ex:
        traceback.print_exception(type(ex), ex, ex.__traceback__)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in login"
        )
    


@router.get('/sso/callback/{provider}', status_code=status.HTTP_200_OK)
async def token(request: Request, response: Response):
    engine = request.app.state.engine
    try:
        provider = request.path_params['provider']
        match provider:
            case "google":
                access_token = await get_google_token(request)
                user_email, provider_id = access_token['userinfo']["email"] , access_token['userinfo']["sub"]
                data = UserinDB(
                    identifier = user_email,
                    email = user_email,
                    provider = "google",
                    provider_id = provider_id
                )
                
            
            case "github":
                access_token = await get_github_token(request.query_params['code'])
                user_info = await get_user_info_github(access_token)
                user_id, username, user_email  = user_info['id'], user_info["login"], user_info['email']
                data = UserinDB(
                    identifier = username,
                    email = user_email,
                    provider = "github",
                    provider_id = user_id
                )

            case _:
                raise PROVIDER_EXCEPTION
            
        user_exists = await users_exists_by_data(engine, data) 
        if not user_exists:
            id = await initialize_user(engine, data)
        else:
            id = await get_user_id_by_data(engine, data)

        local_token = create_access_token(data={"id": id})
        response = await get_user_profile(request, id)
        set_access_cookie(request,response,local_token)
        return response
    

    except PROVIDER_EXCEPTION:
        raise PROVIDER_EXCEPTION

    except OAuthError as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail= e.error
        )
    
    except DATABASE_EXCEPTION as e:
        raise DATABASE_EXCEPTION
    
    except DATABASE_DOWN_EXCEPTION as e:
        raise DATABASE_DOWN_EXCEPTION

    except Exception as e:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail= "Exception in getting token"
        )

    
async def initialize_user(engine, data):
    id = await add_user(engine, data)
    initial_credit = 1000
    await add_credit_for_user(engine, id, initial_credit)
    return id 

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(request:Request, form : OAuth2PasswordRequestForm = Depends()):
    engine = request.app.state.engine
    try:
        hashed_password = get_password_hash(form.password)
        data = UserinDB(**{"identifier": form.username, "provider": "password", "hashed_pw": hashed_password})
        
        user_exists = await users_exists_by_data(engine, data)
        if user_exists:
            raise ALREADY_REGISTERED_EXCEPTION
        
        id = await initialize_user(engine, data)
        
        access_token = create_access_token(
            data={"id": id},
        )

        response = await get_user_profile(request, id)
        set_access_cookie(request,response,access_token)
        return response
    
    except ALREADY_REGISTERED_EXCEPTION:
        raise ALREADY_REGISTERED_EXCEPTION
    
    except DATABASE_EXCEPTION:
        raise DATABASE_EXCEPTION
    
    except DATABASE_DOWN_EXCEPTION:
      raise DATABASE_DOWN_EXCEPTION
   

    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in signup"
        )
    



@router.post("/login", status_code=status.HTTP_200_OK)
async def login_for_access_token(request:Request, form : OAuth2PasswordRequestForm = Depends()):
    engine = request.app.state.engine
    try:
        data = UserinDB(**{"identifier": form.username, "provider": "password"})
        user_exists = await users_exists_by_data(engine, data)
        if not user_exists:
            raise INCORRECT_USERNAME_EXCEPTION
        user_in_db = await get_user_by_data(engine, data)
        id = user_in_db.id

        if not verify_password(form.password, user_in_db.hashed_pw):
            raise INCORRECT_PASSWORD_EXCEPTION
        access_token = create_access_token(
            data={"id": id},
        )
        print(id)

        response = await get_user_profile(request, id)
        return response
    
    except INCORRECT_USERNAME_EXCEPTION:
        raise INCORRECT_USERNAME_EXCEPTION
    
    except DATABASE_EXCEPTION:
        raise DATABASE_EXCEPTION
   
    except DATABASE_DOWN_EXCEPTION:
      raise DATABASE_DOWN_EXCEPTION
   
    except INCORRECT_PASSWORD_EXCEPTION:
        raise INCORRECT_PASSWORD_EXCEPTION

    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in login"
        )

def set_access_cookie(req:Request,res:Response,access_token):
    host=req.headers.get('host')
    res.set_cookie(key="access_token",domain=host.split(':')[0], value=access_token,samesite="none", secure=True, expires=ACCESS_TOKEN_EXPIRE_MINUTES*60)

async def get_current_user_token(request:Request, access_token: Union[str, None] = Cookie(None)):
    if access_token is None:
        raise COOKIE_EXCEPTION
    _ = await get_current_user_id_http(request, access_token)
    return access_token


async def get_current_user_id_ws(websocket: WebSocket, access_token: str):

    engine = websocket.app.state.engine
    if access_token is None:
        raise COOKIE_EXCEPTION

    if await is_token_blacklisted(engine, access_token):
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
    
    user_exists = await users_exists_by_id(engine, id)
    if user_exists:
        return id 
    
    raise CREDENTIALS_EXCEPTION



async def get_current_user_id_http(request: Request, access_token: Union[str, None] = Cookie(None)):

    engine = request.app.state.engine
    if access_token is None:
        raise COOKIE_EXCEPTION

    if await is_token_blacklisted(engine, access_token):
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
    
    user_exists = await users_exists_by_id(engine, id)
    if user_exists:
        return id 
    
    raise CREDENTIALS_EXCEPTION


@router.get('/logout')
async def logout(request:Request, token: str = Depends(get_current_user_token)):
    engine = request.app.state.engine
    try :
        await add_blacklist_token(engine, token)
        response = JSONResponse(content={"result": True}, status_code=200)
        response.delete_cookie("access_token")
        return response 
    
    except DATABASE_EXCEPTION:
        raise DATABASE_EXCEPTION

    except DATABASE_DOWN_EXCEPTION:
      raise DATABASE_DOWN_EXCEPTION
       
    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in logout"
        )

@router.get('/profile')
async def get_user_profile(request:Request, id :int = Depends(get_current_user_id_http)):
    engine = request.app.state.engine

    try:
        data =await get_user_by_id(engine, id)
        profile = {
            "identifier": data.identifier,
            "provider": data.provider,
            "provider_id": data.provider_id,
            "email": data.email
        }
        return JSONResponse(content=profile, status_code=200)
    
    except DATABASE_EXCEPTION:
        raise DATABASE_EXCEPTION
    
    except DATABASE_DOWN_EXCEPTION:
      raise DATABASE_DOWN_EXCEPTION
    
    
    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in getting user profile"
        )
    




# @router.get("/testall")
# async def testall():
#     return await get_all_api_keys()

# @router.get("/usersall")
# async def testall():
#     return await get_all_users()



# # @router.route('/kuber/{endpoint:path}'])
# # if authenticated, requests forwarded to the kuber server
# # @router.get('/kuber/{endpoint:path}')
# # async def forward(request: Request, identifier: str = Depends(get_current_user)):
# #     try:
# #         endpoint = request.path_params['endpoint']
# #         print(f"Forwarding get request to {KUBER_SERVER}/{endpoint}")
        
# #         # async with httpx.AsyncClient() as client:
# #         #     response = await client.get(f"http://localhost:8000/{endpoint}", headers=request.headers)
# #         #     return JSONResponse(content=response.json(), status_code=response.status_code)
# #         print(identifier)
# #         return JSONResponse(content={"result": True, "identifier": identifier}, status_code=200 )
        
# #      except Exception as e:
        # print(e)
# #         print("Could not forward request")
# #         raise KUBER_EXCEPTION
    

# # @router.post('/kuber/{endpoint:path}')
# # async def forward(request: Request, identifier: str = Depends(get_current_user)):
# #     try:
# #         endpoint = request.path_params['endpoint']
# #         print(f"Forwarding post request to {KUBER_SERVER}/{endpoint}")
# #         # async with httpx.AsyncClient() as client:
# #             # response = await client.post(f"http://localhost:8000/{endpoint}", headers=request.headers, data=request.body)
# #             # return JSONResponse(content=response.json(), status_code=response.status_code)
# #         return JSONResponse(content={"result": True}, status_code=200)

# #      except Exception as e:
        # print(e)
# #         print("Could not forward request")
# #         raise KUBER_EXCEPTION
  





# # Implementation of refresh token
# # @router.post('/refresh')
# # async def refresh(request: Request):
# #     try:
# #         form = await request.json()
# #         if form.get('grant_type') == 'refresh_token':
# #             token = form.get('refresh_token')
# #             payload = decodeJWT(token)
# #             email = payload.get('email')
# #             if valid_email_from_db(email):
# #                 return JSONResponse({'result': True, 'access_token': create_access_token(data={"email": email})})
            
# #             else :
# #                 print("Email not found in db")

# #     except JWTError:
# #         print("JWTError")
# #         raise CREDENTIALS_EXCEPTION
# #     raise CREDENTIALS_EXCEPTION



# # async def get_current_user_id_httpentifier(data : UserinDB = Depends(get_current_user_id_http)):
# #     return data.identifier
  

# # Comment out the following lines to test users in db

# # async def add_if_not_in_db(data: UserinDB ):
# #     user_exists  = await users_exists_by_data(data)
# #     if not user_exists:
# #         print("Adding user")
# #         await add_user(data)



# # @router.get("/test")
# # async def test():
# #     data = UserinDB(identifier="tassu", provider="password")
# #     await add_if_not_in_db(data)

