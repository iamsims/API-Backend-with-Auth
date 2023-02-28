from fastapi import APIRouter


from typing import Union
from fastapi import Depends, FastAPI
import httpx
from jose import JWTError

from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from starlette.responses import JSONResponse
from fastapi import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuthError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from starlette.middleware.sessions import SessionMiddleware
from decouple import config

from app.auth.jwt_handler import ALREADY_REGISTERED_EXCEPTION, CREDENTIALS_EXCEPTION, DATABASE_EXCEPTION, INCORRENT_PASSWORD_EXCEPTION, INCORRENT_USERNAME_EXCEPTION
from app.auth.jwt_handler import create_access_token, verify_jwt, decodeJWT, create_refresh_token
from datetime import timedelta
from app.auth.password_handler import get_password_hash, verify_password

from app.controllers.db import add_user, get_all_users, get_user, is_user_in_db, add_blacklist_token, is_token_blacklisted

from app.models.users import UserinDB, UserLoginSchema



router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# OAuth settings
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID') or None
GOOGLE_CLIENT_SECRET =config('GOOGLE_CLIENT_SECRET') or None
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing env variables')

# OAuth settings
GITHUB_CLIENT_ID = config('GITHUB_CLIENT_ID') or None
GITHUB_CLIENT_SECRET =config('GITHUB_CLIENT_SECRET') or None
if GITHUB_CLIENT_ID is None or GITHUB_CLIENT_SECRET is None:
    raise BaseException('Missing env variables')


# Set up oauth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@router.get('/')
def public():
    return {'result': 'This is a public endpoint.'}


@router.route('/login/{provider}')
async def login(request: Request):
    provider = request.path_params['provider']
    match provider:
        case "google":
            redirect_uri = request.url_for('token', provider= "google")  # This creates the url for the /auth endpoint
            return await oauth.google.authorize_redirect(request, redirect_uri)
        case "github":
            return RedirectResponse(url = f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}', status_code = 302) 
        case _:
            return JSONResponse({'result': False, 'message': 'Invalid provider'}, status_code=400)        


async def get_google_token(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        print("oauth error")
        raise CREDENTIALS_EXCEPTION
    return access_token

async def get_github_token(code : str):
    try:
        params = {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code
        }
        headers = { "Accept": "application/json" }
        async with httpx.AsyncClient() as client:
            r = await client.post(url = 'https://github.com/login/oauth/access_token', params=params, headers=headers)
        response_json = r.json()
        # print(response_json)
        access_token = response_json['access_token']

    except:
        print("oauth error")
        raise CREDENTIALS_EXCEPTION
    
    return access_token

async def get_user_info_github(access_token):
    headers = { "Accept": "application/json" } 
    try:
        async with httpx.AsyncClient() as client:
            headers.update({"Authorization": f"Bearer {access_token}"})
            response = await client.get('https://api.github.com/user', headers=headers)
        return response.json()
    
    except:
        raise CREDENTIALS_EXCEPTION

@router.post("/signup")
async def signup(user: UserLoginSchema):
    hashed_password = get_password_hash(user.password)
    data = UserinDB(**{"identifier": user.username, "provider": "password", "hashed_pw": hashed_password, "provider_id": user.username})

    user_exists = await is_user_in_db(data)
    if user_exists:
        raise ALREADY_REGISTERED_EXCEPTION

    await add_user(data)

    access_token = create_access_token(
        data=vars(data),
    )
    return JSONResponse({"result": True, "access_token": access_token, "token_type": "bearer"})


@router.post("/token")
async def login_for_access_token(user: UserLoginSchema):

    data = UserinDB(**{"identifier": user.username, "provider": "password", "provider_id": user.username})
    
    user_exists = await is_user_in_db(data)

    if not user_exists:
        raise INCORRENT_USERNAME_EXCEPTION
    

    user_in_db = await get_user(data)
    if not verify_password(user.password, user_in_db.hashed_pw):
        raise INCORRENT_PASSWORD_EXCEPTION
    
    access_token = create_access_token(
        data=vars(data),
    )

    return JSONResponse({"result": True, "access_token": access_token, "token_type": "bearer"})



@router.route('/token/{provider}')
async def token(request: Request):
    provider = request.path_params['provider']
    match provider:
        case "google":
            try:
                access_token = await get_google_token(request)
                user_email, provider_id = access_token['userinfo']["email"] , access_token['userinfo']["sub"]
                data = {"identifier": user_email, "provider": "google", "provider_id": provider_id}
            except:
                print("Could not get email")
                raise CREDENTIALS_EXCEPTION
            
        case "github":
            try:
                access_token = await get_github_token(request.query_params['code'])
                user_info = await get_user_info_github(access_token)
                user_id, username  = user_info['id'], user_info["login"]
                data = {"provider_id": user_id, "identifier" : username , "provider": "github" }            
            except:
                print("Could not get email")
                raise CREDENTIALS_EXCEPTION
    

    try : 
        data_ = UserinDB(**data) 
        user_exists = await is_user_in_db(data_) 
        if not user_exists:
            await add_user(data_)

    except:
        raise DATABASE_EXCEPTION

    local_token = create_access_token(data=data)
    refresh_token = create_refresh_token(data = data)
    return JSONResponse({'result': True, 'access_token': local_token, "refresh_token": refresh_token})



async def get_current_user_token(token: str = Depends(oauth2_scheme)):
    _ = await get_current_user(token)
    return token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if await is_token_blacklisted(token):
        print("Token is blacklisted")
        raise CREDENTIALS_EXCEPTION
    try:
        payload = decodeJWT(token=token)
        identifier: str = payload.get('identifier')
        provider: str = payload.get('provider')
        provider_id = payload.get('provider_id')

        if identifier is None or provider is None or provider_id is None:
            print("Identifier, provider or provider_id could not be extracted")
            raise CREDENTIALS_EXCEPTION

    except JWTError:
        print("JWT Error")
        raise CREDENTIALS_EXCEPTION

    data = UserinDB(**{"identifier": identifier, "provider": provider, "provider_id": provider_id})
    if await is_user_in_db(data):
        return identifier

    print("Last error, could not find the user in the database")
    raise CREDENTIALS_EXCEPTION
   
  
@router.get('/logout')
async def logout(token: str = Depends(get_current_user_token)):
    try :
        await add_blacklist_token(token)
    except:
        print("Could not add token to blacklist")
        raise DATABASE_EXCEPTION
    
    return {'result': True}

@router.get('/protected')
async def protected(identifier: str = Depends(get_current_user)):
    return {'identifier': identifier}



# Implementation of refresh token
# @router.post('/refresh')
# async def refresh(request: Request):
#     try:
#         form = await request.json()
#         if form.get('grant_type') == 'refresh_token':
#             token = form.get('refresh_token')
#             payload = decodeJWT(token)
#             email = payload.get('email')
#             if valid_email_from_db(email):
#                 return JSONResponse({'result': True, 'access_token': create_access_token(data={"email": email})})
            
#             else :
#                 print("Email not found in db")

#     except JWTError:
#         print("JWTError")
#         raise CREDENTIALS_EXCEPTION
#     raise CREDENTIALS_EXCEPTION





# Comment out the following lines to test users in db

# async def add_if_not_in_db(data: UserinDB ):
#     user_exists  = await is_user_in_db(data)
#     if not user_exists:
#         print("Adding user")
#         await add_user(data)


# @router.get("/testall")
# async def testall():
#     return await get_all_users()

# @router.get("/test")
# async def test():
#     data = UserinDB(identifier="tassu", provider="password")
#     await add_if_not_in_db(data)

