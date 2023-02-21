import copy
import os
import calendar
import uuid
from datetime import timedelta, datetime
from typing import Any, Coroutine, List, Callable

import requests
from fastapi import HTTPException, Depends
from fastapi_mail import ConnectionConfig
from jose import ExpiredSignatureError, jwt, JWTError
from loguru import logger
from starlette.responses import Response

from app.auth.token import get_refresh_token, get_token
from app.common.crypto import Crypto
from app.constants import message_constants, app_constants
from app.exceptions.forbidden_exception import ForbiddenException
from app.models.dtos.auth import User
from app.models.schemas.credentials import Provider
from app.repositories import credentials_repository
from app.services.cookie_service import set_token_cookie
from app.services.user_service import UserService
from app.settings import configs
from app.utils.google_utils import credentials_to_dict, dict_to_credentials

crypto = Crypto()

api_settings = configs.api_settings

jwt_secret = api_settings.jwt_secret
host = api_settings.host

def get_current_user(required_roles: List[str] = None) -> Callable[[Response, str, str], Coroutine[Any, Any, User]]:
    """ Returns the current user based on an access token. Optionally verifies roles are possessed by the user

    Args:
        required_roles List[str]: List of role names required for this endpoint

    Returns:
        User: Decoded JWT content

    Raises:
        ExpiredSignatureError: If the token is expired (exp > datetime.now())
        JWTError: If decoding fails or the signature is invalid
        JWTClaimsError: If any claim is invalid
        HTTPException: If any role required is not contained within the roles of the users
    """

    async def refresh_token(token: str):
        if token is None:
            raise HTTPException(status_code=401, detail=message_constants.no_refresh_token_error)
        decoded_token = jwt.decode(token, configs.api_settings.jwt_secret, algorithms=["HS256"])
        user = await UserService.get_user_by_id(user_id=decoded_token['id'])
        decoded_token['roles'] = user.roles
        return decoded_token

    async def current_user(response: Response, token: str, r_token: str) -> User:
        """ Decodes and verifies a JWT to get the current user

        Args:
            token OAuth2PasswordBearer: Access token in `Authorization` HTTP-header

        Returns:
            OIDCUser: Decoded JWT content

        Raises:
            ExpiredSignatureError: If the token is expired (exp > datetime.now())
            JWTError: If decoding fails or the signature is invalid
            JWTClaimsError: If any claim is invalid
            HTTPException: If any role required is not contained within the roles of the users
        """
        if token is None:
            raise JWTError(message_constants.unauthorized_403)

        try:
            decoded_token = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            decoded_token['roles'] = decoded_token['roles'].split(",")
        except ExpiredSignatureError:
            decoded_token = await refresh_token(r_token)
            set_tokens_to_response(User(**decoded_token), response)
        user = User.parse_obj(decoded_token)
        credentials = await credentials_repository.get_all_credentials(user.sub)
        if credentials:
            user.services = [credential.provider for credential in credentials]
        else:
            user.services = []
        if required_roles:
            for role in required_roles:
                if role not in user.roles:
                    raise ForbiddenException(f'Role "{role}" is required to perform this action')
        return user

    return current_user


async def get_user_if_logged_in(response: Response, token: str = Depends(get_token),
                                r_token=Depends(get_refresh_token)):
    try:
        return await get_current_user()(response, token, r_token)
    except Exception as e:
        return None


def get_google_token() -> Callable[[Response, User], Any]:
    async def inner(response: Response, user: User):
        try:
            db_credentials = await credentials_repository.get_credential(email=user.sub, provider=Provider.GOOGLE)
            if not db_credentials:
                raise HTTPException(status_code=401, detail="Not connected to google service.")
            credentials = dict_to_credentials(db_credentials.credentials)
            expiry = credentials.expiry
            current_date = datetime.now()
            if expiry < current_date:
                data = {
                    "client_id": credentials.client_id,
                    "client_secret": credentials.client_secret,
                    "refresh_token": credentials.refresh_token,
                    "grant_type": "refresh_token"
                }
                r = requests.post(credentials.token_uri, data=data)
                new_token_res = r.json()
                new_credentials = copy.deepcopy(credentials)
                new_credentials.token = new_token_res['access_token']
                new_credentials.expiry = current_date + timedelta(seconds=new_token_res['expires_in'])
                json_credentials = credentials_to_dict(credentials=new_credentials)

                response.set_cookie(key="state", value=str(db_credentials.state))
                db_credentials = await credentials_repository.save_credentials(user.sub, json_credentials,
                                                                               db_credentials.state,
                                                                               provider=Provider.GOOGLE)
                return db_credentials
        except HTTPException as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail)
        except Exception as error:
            logger.error(error)
        return None

    return inner


async def get_logged_user(response: Response, token: str = Depends(get_token),
                          r_token: str = Depends(get_refresh_token)) -> User:
    return await get_current_user()(response, token, r_token)


async def get_admin(response: Response, token: str = Depends(get_token), r_token=Depends(get_refresh_token)):
    return await get_current_user(["ADMIN"])(response, token, r_token)


async def get_logged_google_user(response: Response, user: 'User' = Depends(get_logged_user)):
    return await get_google_token()(response, user)


def get_expiry_epoch_after(time_delta: timedelta = timedelta()):
    return calendar.timegm((datetime.utcnow() + time_delta).utctimetuple())


def set_token_to_response(user: User, expiry_after: timedelta, cookie_key: str, response: Response):
    expiry = get_expiry_epoch_after(expiry_after)
    token = jwt.encode(
        {
            'id': user.id,
            'sub': user.sub,
            'roles': ",".join(user.roles),
            'exp': expiry,
            'jti': str(uuid.uuid4())},
        jwt_secret,
        algorithm="HS256")
    set_token_cookie(response, cookie_key, token)


def set_access_token_to_response(user: User, response: Response):
    set_token_to_response(user,
                          timedelta(minutes=api_settings.access_token_expiry_minutes),
                          app_constants.authorization,
                          response)


def set_refresh_token_to_response(user: User, response: Response):
    set_token_to_response(user,
                          timedelta(days=api_settings.refresh_token_expiry_days),
                          app_constants.refresh_token,
                          response)


def set_tokens_to_response(user: User, response: Response):
    set_access_token_to_response(user=user, response=response)
    set_refresh_token_to_response(user=user, response=response)
