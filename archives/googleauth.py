from typing import Union
from fastapi import Depends, FastAPI
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

# from db import add_blacklist_token, is_token_blacklisted 



FAKE_DB = {
    "simrankc347@gmail.com": {
    }
}

def valid_email_from_db(email):
    return email in FAKE_DB


class TokenData:
    email : Union[str, None] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# OAuth settings
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID') or None
GOOGLE_CLIENT_SECRET =config('GOOGLE_CLIENT_SECRET') or None
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing env variables')


SECRET_KEY = config('SECRET_KEY') or None
if SECRET_KEY is None:
    raise 'Missing SECRET_KEY'

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


# Set up oauth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@app.get('/')
def public():
    return {'result': 'This is a public endpoint.'}


@app.route('/login')
async def login(request: Request):
    redirect_uri = request.url_for('token')  # This creates the url for the /auth endpoint
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.route('/token')
async def token(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        print("oauth error  ")
        raise CREDENTIALS_EXCEPTION
    user_email = access_token['userinfo']["email"]
    #TODO : Check if user is in db, if not, add info in db
    # if user_email not in FAKE_DB:
    # if valid_email_from_db(user_email):
    local_token = create_access_token(data={"email": user_email})
    refresh_token = create_refresh_token(data = {"email": user_email})
    return JSONResponse({'result': True, 'access_token': local_token, "refresh_token": refresh_token})

    print("Last error, email might not have been registered")
    raise CREDENTIALS_EXCEPTION


async def get_current_user_token(token: str = Depends(oauth2_scheme)):
    _ = get_current_user(token)
    return token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if is_token_blacklisted(token):
        print("Token is blacklisted")
        raise CREDENTIALS_EXCEPTION
    try:
        payload = decodeJWT(token=token)
        email: str = payload.get('email')
        if email is None:
            print("Email could not be extracted")
            raise CREDENTIALS_EXCEPTION
    except JWTError:
        print("JWT Error")
        raise CREDENTIALS_EXCEPTION

    if valid_email_from_db(email):
        return email

    print("Last error, Email might not be found in db")
    raise CREDENTIALS_EXCEPTION
   
  
@app.get('/logout')
def logout(token: str = Depends(get_current_user_token)):
    if add_blacklist_token(token):
        return JSONResponse({'result': True})
    raise CREDENTIALS_EXCEPTION


@app.get('/protected')
async def protected(current_email: str = Depends(get_current_user)):
    return {'email': current_email}


@app.post('/refresh')
async def refresh(request: Request):
    try:
        form = await request.json()
        if form.get('grant_type') == 'refresh_token':
            token = form.get('refresh_token')
            payload = decodeJWT(token)
            email = payload.get('email')
            if valid_email_from_db(email):
                return JSONResponse({'result': True, 'access_token': create_access_token(data={"email": email})})
            
            else :
                print("Email not found in db")

    except JWTError:
        print("JWTError")
        raise CREDENTIALS_EXCEPTION
    raise CREDENTIALS_EXCEPTION

