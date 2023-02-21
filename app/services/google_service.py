import json

import google_auth_oauthlib
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError
from urllib import parse
from loguru import logger

from app.common.crypto import Crypto
from fastapi import HTTPException, Request

from app.models.schemas.user import UserDocument
from app.settings import configs

from oauthlib.oauth1 import InvalidClientError
from oauthlib.oauth2 import InvalidGrantError
from googleapiclient.discovery import build

crypto = Crypto()
google_settings = configs.google_settings

client_config = {
    "web": {
        "client_id": google_settings.client_id,
        "project_id": google_settings.project_id,
        "auth_uri": google_settings.auth_uri,
        "token_uri": google_settings.token_uri,
        "auth_provider_x509_cert_url": google_settings.auth_provider_x509_cert_url,
        "client_secret": google_settings.client_secret,
        "redirect_uris": google_settings.redirect_uris.split(','),
        "javascript_origins": google_settings.javascript_origins.split(',')
    }
}


def authenticate_google(client_referer_url: str):
    state_json = json.dumps({"client_referer_url": client_referer_url})
    state = crypto.encrypt(state_json)
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_config,
        scopes="https://www.googleapis.com/auth/userinfo.email openid"
    )
    flow.redirect_uri = configs.google_settings.basic_auth_redirect
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        state=state,
        include_granted_scopes='false'
    )
    return authorization_url


def fetch_basic_token(auth_code: str, state):
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_config,
        scopes="https://www.googleapis.com/auth/userinfo.email openid",
        state=state
    )
    flow.redirect_uri = configs.google_settings.basic_auth_redirect
    try:
        flow.fetch_token(authorization_response=auth_code)
    except Exception as e:
        logger.info("Failed to fetch google token")
        logger.error(e.with_traceback(None))
        return None
    credentials = flow.credentials
    return credentials


async def get_google_user(credentials):
    try:
        oauth_service = build(serviceName='oauth2', version="v2", credentials=credentials)
        return oauth_service.userinfo().get().execute()
    except HttpError as error:
        raise HTTPException(status_code=error.status_code, detail=error.error_details)
    except RefreshError:
        raise HTTPException(status_code=401, detail="Google auth token refresh error.")
    except InvalidClientError as error:
        raise HTTPException(status_code=401, detail="Google auth invalid client error.")
    except AttributeError:
        raise HTTPException(status_code=401, detail="State not found. Connect with google services.")
    except InvalidGrantError as e:
        raise HTTPException(401, "Invalid Grant error.")


async def basic_auth_callback(request: Request):
    try:
        tmp = str(request.url)
        authorization_response = tmp if tmp[0:5] == "https" else tmp.replace(tmp[0:4], "https", 1)
        query = parse.urlparse(authorization_response).query
        res = dict(parse.parse_qsl(query))
        state = res.get('state')
        credentials = fetch_basic_token(auth_code=authorization_response, state=state)
        state_json = json.loads(crypto.decrypt(state))
        client_referer_url = state_json['client_referer_url']
        if credentials is None:
            return client_referer_url, None
        user = await get_google_user(credentials)
        user_document = await UserDocument.find_one({'email': user['email']})
        if user_document is None:
            user_document = UserDocument(email=user['email'],
                                         first_name=user.get('given_name'),
                                         last_name=user.get('family_name'),
                                         verified_email=user.get('verified_email'),
                                         profile_picture=user.get('picture'),
                                         username=user.get('name'))
            await user_document.save()
        token_user = user_document.dict()
        token_user['id'] = str(user_document.id)
        return client_referer_url, token_user
    except InvalidGrantError:
        raise HTTPException(status_code=401, detail="Invalid Oauth2 Grant")
    except HttpError as error:
        raise HTTPException(status_code=error.status_code, detail=error.error_details)
    except RefreshError:
        raise HTTPException(status_code=401, detail="Google auth token refresh error.")
    except InvalidClientError as error:
        raise HTTPException(status_code=401, detail="Google auth invalid client error.")
    except AttributeError:
        raise HTTPException(status_code=401, detail="State not found. Connect with google services.")
