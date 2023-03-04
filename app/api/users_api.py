from fastapi import APIRouter, Depends, status 

import httpx
from jose import JWTError
from urllib.parse import quote
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from starlette.responses import JSONResponse
from fastapi import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuthError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from decouple import config

from app.constants.exceptions import ALREADY_REGISTERED_EXCEPTION, CREDENTIALS_EXCEPTION, DATABASE_EXCEPTION, INCORRENT_PASSWORD_EXCEPTION, INCORRENT_USERNAME_EXCEPTION, KUBER_EXCEPTION
from app.auth.jwt_handler import create_access_token, decodeJWT, create_refresh_token
from datetime import timedelta
from app.auth.password_handler import get_password_hash, verify_password

from app.controllers.db import add_user, get_user, is_user_in_db, add_blacklist_token, is_token_blacklisted, get_all_users

from app.models.users import UserinDB, UserLoginSchema

from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

# OAuth settings
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID') or None
GOOGLE_CLIENT_SECRET =config('GOOGLE_CLIENT_SECRET') or None
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing env variables for google auth')


KUBER_SERVER = config('KUBER_SERVER') or None
if KUBER_SERVER is None:
    raise BaseException('Missing env variables for kuber server')

# OAuth settings
GITHUB_CLIENT_ID = config('GITHUB_CLIENT_ID') or None
GITHUB_CLIENT_SECRET =config('GITHUB_CLIENT_SECRET') or None
if GITHUB_CLIENT_ID is None or GITHUB_CLIENT_SECRET is None:
    raise BaseException('Missing env variables for github auth')


# Set up oauth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)




router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get('/login/{provider}')
async def login(request: Request):
    provider = request.path_params['provider']
    match provider:
        case "google":
            redirect_uri = request.url_for('token', provider= "google")  # This creates the url for the /auth endpoint
            return await oauth.google.authorize_redirect(request, redirect_uri)
        case "github":
            scope = "read:user user:email"
            encoded_scope = quote(scope)
            return RedirectResponse(url = f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope={encoded_scope}', status_code = 302) 
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
        print(response_json)
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
            response_json = response.json()
            if response_json['email'] is None:
                email_response = await client.get('https://api.github.com/user/emails', headers=headers)
                response_json['email'] = email_response.json()[0]['email']

        return response_json
    
    except:
        raise CREDENTIALS_EXCEPTION

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(form : OAuth2PasswordRequestForm = Depends()):
    hashed_password = get_password_hash(form.password)
    data = UserinDB(**{"identifier": form.username, "provider": "password", "hashed_pw": hashed_password, "provider_id": form.username})

    user_exists = await is_user_in_db(data)
    if user_exists:
        raise ALREADY_REGISTERED_EXCEPTION

    await add_user(data)

    access_token = create_access_token(
        data=vars(data),
    )
    return JSONResponse({"result": True, "access_token": access_token, "token_type": "bearer"})


@router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(form : OAuth2PasswordRequestForm = Depends()):

    data = UserinDB(**{"identifier": form.username, "provider": "password", "provider_id": form.username})
    
    user_exists = await is_user_in_db(data)

    if not user_exists:
        raise INCORRENT_USERNAME_EXCEPTION
    

    user_in_db = await get_user(data)
    if not verify_password(form.password, user_in_db.hashed_pw):
        raise INCORRENT_PASSWORD_EXCEPTION
    
    access_token = create_access_token(
        data=vars(data),
    )

    return JSONResponse({"result": True, "access_token": access_token, "token_type": "bearer"})



@router.get('/token/{provider}')
async def token(request: Request):
    provider = request.path_params['provider']
    match provider:
        case "google":
            try:
                access_token = await get_google_token(request)
                user_email, provider_id = access_token['userinfo']["email"] , access_token['userinfo']["sub"]
                
                data = {"identifier": user_email, "email": user_email, "provider": "google", "provider_id": provider_id}
                print(data)
            except:
                print("Could not get email")
                raise CREDENTIALS_EXCEPTION
            
        case "github":
            try:
                access_token = await get_github_token(request.query_params['code'])
                user_info = await get_user_info_github(access_token)
                # return user_info
                user_id, username, user_email  = user_info['id'], user_info["login"], user_info['email']
                data = {"provider_id": user_id, "email": user_email, "identifier" : username , "provider": "github" }            
            except:
                print("Could not get email")
                raise CREDENTIALS_EXCEPTION
    

    try : 
        data_ = UserinDB(**data) 
        data.pop('email')
        user_exists = await is_user_in_db(data_) 
        if not user_exists:
            await add_user(data_)

    except:
        raise DATABASE_EXCEPTION
    
    local_token = create_access_token(data=data)
    refresh_token = create_refresh_token(data = data)
    return JSONResponse({'result': True, 'access_token': local_token, "token_type": "bearer"})



async def get_current_user_token(token: str = Depends(oauth2_scheme)):
    _ = await get_current_user_info(token)
    return token


async def get_current_user_info(token: str = Depends(oauth2_scheme)):
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
        return data
    
    raise CREDENTIALS_EXCEPTION


async def get_current_user_identifier(data : UserinDB = Depends(get_current_user_info)):
    print(data)
    return data.identifier
    
  
@router.get('/logout')
async def logout(token: str = Depends(get_current_user_token)):
    try :
        await add_blacklist_token(token)
    except:
        print("Could not add token to blacklist")
        raise DATABASE_EXCEPTION
    
    return {'result': True}


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
        raise DATABASE_EXCEPTION


@router.route('/{endpoint:path}', methods=['GET', 'POST'])
async def reverse_proxy(request: Request):
    if request.headers.get('authorization'):
        token = request.headers.get('authorization').split(" ")[1]

    else:
        raise CREDENTIALS_EXCEPTION
    
    user = await get_current_user_info(token)
    if (user):
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
    
    else:
        raise CREDENTIALS_EXCEPTION
    

    



# @router.route('/kuber/{endpoint:path}'])
# if authenticated, requests forwarded to the kuber server
# @router.get('/kuber/{endpoint:path}')
# async def forward(request: Request, identifier: str = Depends(get_current_user)):
#     try:
#         endpoint = request.path_params['endpoint']
#         print(f"Forwarding get request to {KUBER_SERVER}/{endpoint}")
        
#         # async with httpx.AsyncClient() as client:
#         #     response = await client.get(f"http://localhost:8000/{endpoint}", headers=request.headers)
#         #     return JSONResponse(content=response.json(), status_code=response.status_code)
#         print(identifier)
#         return JSONResponse(content={"result": True, "identifier": identifier}, status_code=200 )
        
#     except:
#         print("Could not forward request")
#         raise KUBER_EXCEPTION
    

# @router.post('/kuber/{endpoint:path}')
# async def forward(request: Request, identifier: str = Depends(get_current_user)):
#     try:
#         endpoint = request.path_params['endpoint']
#         print(f"Forwarding post request to {KUBER_SERVER}/{endpoint}")
#         # async with httpx.AsyncClient() as client:
#             # response = await client.post(f"http://localhost:8000/{endpoint}", headers=request.headers, data=request.body)
#             # return JSONResponse(content=response.json(), status_code=response.status_code)
#         return JSONResponse(content={"result": True}, status_code=200)

#     except:
#         print("Could not forward request")
#         raise KUBER_EXCEPTION
  





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

