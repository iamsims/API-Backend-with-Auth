# import datetime
# import secrets
# import time
# import traceback
# from typing import Union
# from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, WebSocket, status 

# from urllib.parse import quote, urlparse
# from starlette.responses import JSONResponse
# from fastapi import Request
# from starlette.responses import RedirectResponse
# from authlib.integrations.starlette_client import OAuthError
# from fastapi.security import OAuth2PasswordRequestForm
# from app.api.ws_proxy import HLS_COST_PER_MS



# # from app.constants.exceptions import ALREADY_REGISTERED_EXCEPTION, COOKIE_EXCEPTION, CREDENTIALS_EXCEPTION, DATABASE_EXCEPTION, GITHUB_OAUTH_EXCEPTION, GOOGLE_OAUTH_EXCEPTION, INCORRENT_PASSWORD_EXCEPTION, INCORRENT_USERNAME_EXCEPTION, KUBER_EXCEPTION, LOGIN_EXCEPTION, PROVIDER_EXCEPTION, SIGNUP_EXCEPTION, CustomException
# from app.auth.jwt_handler import create_access_token, decodeJWT
# from app.auth.password_handler import get_password_hash, verify_password
# from app.controllers.db import add_blacklist_token, add_log_entry, create_credit_for_user, add_user, decrement_credit_for_user, get_credit_for_user, get_logs, get_user_by_data, get_user_by_id, get_user_id_by_data, is_token_blacklisted, users_exists_by_data, users_exists_by_id


# from app.models.users import UserinDB

# from app.constants.token import ACCESS_TOKEN_EXPIRE_MINUTES
# from app.auth.oauth import get_github_token, get_google_token, get_user_info_github, oauth, GITHUB_CLIENT_ID
# from app.controllers.db import add_user, get_user_by_id
# from prisma.models import logs



# router = APIRouter()

# @router.get('/')
# async def test(request : Request):
#     data = UserinDB(
#         identifier='test',
#         email = "a",
#         hashed_pw = 'a',
#         provider = 'a',
#         provider_id = 'a',
#     )

#     start_time = time.time()
#     end_time = time.time()
#     ip_address = request.client.host
#     duration = int(round((end_time - start_time)*1000))
#     cost = duration * HLS_COST_PER_MS
#     id = 8
#     start_time = int(round(start_time))

#     # await add_log_entry( 
#     #     start_time=start_time,
#     #     duration=duration,
#     #     cost = cost,
#     #     ip_address=ip_address,
#     #     user_id=id,
#     #     status_code=200,        
#     # )


#     await decrement_credit_for_user(8, cost)
#     credit = await get_credit_for_user(8)
#     logs = await get_logs(user_id=8, 
#                           page = 3)
#     print(logs)
#     return {'credit': credit, "user": 8, "cost" : cost}
