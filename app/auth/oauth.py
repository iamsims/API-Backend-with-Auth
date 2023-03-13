



from authlib.integrations.starlette_client import OAuth
from fastapi import Request
import httpx
from starlette.config import Config
from decouple import config

# OAuth settings
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID') or None
GOOGLE_CLIENT_SECRET =config('GOOGLE_CLIENT_SECRET') or None
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing env variables for google auth')



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




async def get_google_token(request: Request):
    access_token = await oauth.google.authorize_access_token(request)
    return access_token


async def get_github_token(code : str):
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
    return access_token

async def get_user_info_github(access_token):
    headers = { "Accept": "application/json" } 
    async with httpx.AsyncClient() as client:
        headers.update({"Authorization": f"Bearer {access_token}"})
        response = await client.get('https://api.github.com/user', headers=headers)
        response_json = response.json()
        if response_json['email'] is None:
            email_response = await client.get('https://api.github.com/user/emails', headers=headers)
            response_json['email'] = email_response.json()[0]['email']

    return response_json
    