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
from app.auth.api_key import get_api_key

from app.constants.exceptions import ALREADY_REGISTERED_EXCEPTION, COOKIE_EXCEPTION, CREDENTIALS_EXCEPTION, INCORRECT_PASSWORD_EXCEPTION, INCORRECT_USERNAME_EXCEPTION, KUBER_EXCEPTION, PROVIDER_EXCEPTION
# from app.constants.exceptions import ALREADY_REGISTERED_EXCEPTION, COOKIE_EXCEPTION, CREDENTIALS_EXCEPTION, DATABASE_EXCEPTION, GITHUB_OAUTH_EXCEPTION, GOOGLE_OAUTH_EXCEPTION, INCORRENT_PASSWORD_EXCEPTION, INCORRENT_USERNAME_EXCEPTION, KUBER_EXCEPTION, LOGIN_EXCEPTION, PROVIDER_EXCEPTION, SIGNUP_EXCEPTION, CustomException
# from app.constants.exceptions import PROVIDER_EXCEPTION, MyException
from app.auth.jwt_handler import create_access_token, decodeJWT, create_refresh_token
from datetime import timedelta
from app.auth.password_handler import get_password_hash, verify_password

from app.controllers.db import add_user, get_user, is_user_in_db, add_blacklist_token, is_token_blacklisted, get_all_users

from app.models.users import UserinDB, UserLoginSchema

from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from app.constants.token import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES


KUBER_SERVER = config('KUBER_SERVER') or None
if KUBER_SERVER is None:
    raise BaseException('Missing env variables for kuber server')


router = APIRouter()


from app.auth.oauth import get_github_token, get_google_token, get_user_info_github, oauth

@router.get('/login/{provider}')
async def login(request: Request):
    provider = request.path_params['provider']
    try:
        match provider:
            case "google":
                redirect_uri = request.url_for('token', provider= "google")  # This creates the url for the /auth endpoint
                return await oauth.google.authorize_redirect(request, redirect_uri)
    
            case "github":
                scope = "read:user user:email"
                encoded_scope = quote(scope)
                return RedirectResponse(url = f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope={encoded_scope}', status_code = 302) 
                
            case _:
                raise PROVIDER_EXCEPTION
            
    except PROVIDER_EXCEPTION:
        raise PROVIDER_EXCEPTION

    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in login"
        )
    

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(form : OAuth2PasswordRequestForm = Depends()):
    try:
        hashed_password = get_password_hash(form.password)
        data = UserinDB(**{"identifier": form.username, "provider": "password", "hashed_pw": hashed_password, "provider_id": form.username})
        
        user_exists = await is_user_in_db(data)
        if user_exists:
            raise ALREADY_REGISTERED_EXCEPTION
        
        await add_user(data)
        
        access_token = create_access_token(
            data=vars(data),
        )
        response = JSONResponse(content={"result": True}, status_code=200)
        response.set_cookie(key="access_token", value=access_token, httponly=True, expires=ACCESS_TOKEN_EXPIRE_MINUTES*60)
        return response
    
    except ALREADY_REGISTERED_EXCEPTION:
        raise ALREADY_REGISTERED_EXCEPTION

    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in signup"
        )


@router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(form : OAuth2PasswordRequestForm = Depends()):
    try:
        data = UserinDB(**{"identifier": form.username, "provider": "password", "provider_id": form.username})
        user_exists = await is_user_in_db(data)
        if not user_exists:
            raise INCORRECT_USERNAME_EXCEPTION
        user_in_db = await get_user(data)
        if not verify_password(form.password, user_in_db.hashed_pw):
            raise INCORRECT_PASSWORD_EXCEPTION
        access_token = create_access_token(
            data=vars(data),
        )

        response = JSONResponse(content={"result": True}, status_code=200)
        response.set_cookie(key="access_token", value=access_token, httponly=True, expires=ACCESS_TOKEN_EXPIRE_MINUTES*60)
        return response
    
    except INCORRECT_USERNAME_EXCEPTION as e:
        raise INCORRECT_USERNAME_EXCEPTION
    

    except INCORRECT_PASSWORD_EXCEPTION as e:
        raise INCORRECT_PASSWORD_EXCEPTION

    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in login"
        )



@router.get('/token/{provider}')
async def token(request: Request, response: Response):
    try:
        provider = request.path_params['provider']
        match provider:
            case "google":
                access_token = await get_google_token(request)
                user_email, provider_id = access_token['userinfo']["email"] , access_token['userinfo']["sub"]
                data = {"identifier": user_email, "email": user_email, "provider": "google", "provider_id": provider_id}
            
            case "github":
                access_token = await get_github_token(request.query_params['code'])
                user_info = await get_user_info_github(access_token)
                user_id, username, user_email  = user_info['id'], user_info["login"], user_info['email']
                data = {"provider_id": user_id, "email": user_email, "identifier" : username , "provider": "github" }            

            case _:
                raise PROVIDER_EXCEPTION
            
        data_ = UserinDB(**data) 
        data.pop('email')
        user_exists = await is_user_in_db(data_) 
        if not user_exists:
            await add_user(data_)

    
        local_token = create_access_token(data=data)
        response = JSONResponse(content={"result": True}, status_code=200)
        response.set_cookie(key="access_token", value=local_token, httponly=True, expires=ACCESS_TOKEN_EXPIRE_MINUTES*60)
        return response
    

    except PROVIDER_EXCEPTION:
        raise PROVIDER_EXCEPTION

    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in obtaining token"
        )
    


async def get_current_user_token(access_token: Union[str, None] = Cookie(None)):
    if access_token is None:
        raise COOKIE_EXCEPTION
    _ = await get_current_user_info(access_token)
    return access_token



async def get_current_user_info(access_token: Union[str, None] = Cookie(None)):
    if access_token is None:
        raise COOKIE_EXCEPTION

    if await is_token_blacklisted(access_token):
        print("Token is blacklisted")
        raise CREDENTIALS_EXCEPTION
    payload = decodeJWT(token=access_token)
    identifier: str = payload.get('identifier')
    provider: str = payload.get('provider')
    provider_id = payload.get('provider_id')
    
    if identifier is None or provider is None or provider_id is None:
        print("Identifier, provider or provider_id could not be extracted")
        raise CREDENTIALS_EXCEPTION
    data = UserinDB(**{"identifier": identifier, "provider": provider, "provider_id": provider_id})
    
    if await is_user_in_db(data):
        return data
    
    raise CREDENTIALS_EXCEPTION


@router.get('/logout')
async def logout(token: str = Depends(get_current_user_token)):
    try :
        await add_blacklist_token(token)
        return JSONResponse(content={"result": True}, status_code=200)

    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in logout"
        )


@router.get("/generate_api_key")
async def api_key(data : UserinDB = Depends(get_current_user_info)):
    try:
        api_key = await get_api_key(data)
        return JSONResponse(content={"result": True, "api_key": api_key}, status_code=200)
    
    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in ksks generating api key"
        )

@router.get('/user_profile')
async def get_user_profile(data : UserinDB = Depends(get_current_user_info)):
    try:
        all =await get_user(data)
        profile = {
            "identifier": all.identifier,
            "provider": all.provider,
            "provider_id": all.provider_id,
            "email": all.email
        }
        return profile
    
    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in getting user profile"
        )


@router.route('/{endpoint:path}', methods=['GET', 'POST'])
async def reverse_proxy(request: Request):
    try:
        if request.cookies.get('access_token'):
            token = request.cookies.get('access_token')
            print(token)
        else:
            raise COOKIE_EXCEPTION
    
        user = await get_current_user_info(token)
        if (user):
            try:
                client = request.app.state.client
                url = httpx.URL(path=request.url.path, query=request.url.query.encode('utf-8'))
                print(url)

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

            except:
                raise KUBER_EXCEPTION
    
        else:
            raise CREDENTIALS_EXCEPTION
        

    except COOKIE_EXCEPTION or CREDENTIALS_EXCEPTION or KUBER_EXCEPTION as e:
        raise HTTPException(
        status_code=e.status_code,
        detail=e.detail,
    )

    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in reverse proxy"
        )

    

    



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
        
# #     except:
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

# #     except:
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



# # async def get_current_user_identifier(data : UserinDB = Depends(get_current_user_info)):
# #     return data.identifier
  

# # Comment out the following lines to test users in db

# # async def add_if_not_in_db(data: UserinDB ):
# #     user_exists  = await is_user_in_db(data)
# #     if not user_exists:
# #         print("Adding user")
# #         await add_user(data)


# # @router.get("/testall")
# # async def testall():
# #     return await get_all_users()

# # @router.get("/test")
# # async def test():
# #     data = UserinDB(identifier="tassu", provider="password")
# #     await add_if_not_in_db(data)

