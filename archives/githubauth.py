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
from fastapi.security import OAuth2PasswordBearer

from starlette.middleware.sessions import SessionMiddleware
from decouple import config

from app.auth.jwt_handler import CREDENTIALS_EXCEPTION, create_refresh_token
from app.auth.jwt_handler import create_access_token, verify_jwt, decodeJWT
from datetime import timedelta

from db import add_blacklist_token, is_token_blacklisted 


GITHUB_CLIENT_ID = config('GITHUB_CLIENT_ID') or None
GITHUB_CLIENT_SECRET =config('GITHUB_CLIENT_SECRET') or None
if GITHUB_CLIENT_ID is None or GITHUB_CLIENT_SECRET is None:
    raise BaseException('Missing env variables')



FAKE_DB = {
    "33872291" :{
        "login" :"iamsims", 
        "id" : "33872291"
    }, 

}

def valid_id_from_db(id):
    return id in FAKE_DB


class TokenData:
    email : Union[str, None] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




SECRET_KEY = config('SECRET_KEY') or None
if SECRET_KEY is None:
    raise 'Missing SECRET_KEY'

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@app.get('/')
def public():
    return {'result': 'This is a public endpoint.'}


# makes a login request to github and redirects to the token endpoint
@app.get('/login')
async def login():
    return RedirectResponse(url = f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}', status_code = 302)



# gets the token from github and returns a local token
@app.get('/token')
async def token( code: str ):
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
        async with httpx.AsyncClient() as client:
            headers.update({"Authorization": f"Bearer {access_token}"})
            response = await client.get('https://api.github.com/user', headers=headers)

    except:
        raise CREDENTIALS_EXCEPTION

        
    response_json =  response.json()
    id, login = response_json['id'], response_json['login']
    FAKE_DB.update({id: {"id": id, "login": login}})
    # TODO : add user to db if not exist already 
    local_token = create_access_token(data={"id": id , "login": login})
    refresh_token = create_refresh_token(data = {"id": id , "login": login})
    return JSONResponse({'result': True, 'access_token': local_token, 'refresh_token': refresh_token})



async def get_current_user_token(token: str = Depends(oauth2_scheme)):
    _ = get_current_user(token)
    return token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if is_token_blacklisted(token):
        print("Token is blacklisted")
        raise CREDENTIALS_EXCEPTION
    try:
        payload = decodeJWT(token=token)
        id: str = payload.get('id')
        if id is None:
            print("ID could not be extracted from token")
            raise CREDENTIALS_EXCEPTION
    except JWTError:
        print("JWT Error")
        raise CREDENTIALS_EXCEPTION

    if valid_id_from_db(id):
        return id

    print("Last error, Email might not be found in db")
    raise CREDENTIALS_EXCEPTION
   
  
@app.get('/logout')
def logout(token: str = Depends(get_current_user_token)):
    if add_blacklist_token(token):
        return JSONResponse({'result': True})
    raise CREDENTIALS_EXCEPTION


@app.get('/protected')
async def protected(current_id: str = Depends(get_current_user)):
    return {'id': current_id}


@app.post('/refresh')
async def refresh(request: Request):
    try:
        form = await request.json()
        if form.get('grant_type') == 'refresh_token':
            token = form.get('refresh_token')
            payload = decodeJWT(token)
            id = payload.get('id')
            if valid_id_from_db(id):
                return JSONResponse({'result': True, 'access_token': create_access_token(data={"id": id , "login": login})})
            else :
                print("id not found in db")

    except JWTError:
        print("JWTError")
        raise CREDENTIALS_EXCEPTION
    raise CREDENTIALS_EXCEPTION

