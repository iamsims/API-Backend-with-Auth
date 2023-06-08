import datetime
import secrets
import traceback
from typing import Union
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, WebSocket, status 

from urllib.parse import quote, urlparse
from starlette.responses import JSONResponse
from fastapi import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuthError
from fastapi.security import OAuth2PasswordRequestForm
from app.api.authenticate import get_current_user_id_http, get_current_user_token



from app.constants.exceptions import ALREADY_REGISTERED_EXCEPTION, COOKIE_EXCEPTION, CREDENTIALS_EXCEPTION, CREDIT_NOT_ENOUGH_EXCEPTION, DATABASE_DOWN_EXCEPTION, DATABASE_EXCEPTION, ENDPOINT_DOES_NOT_EXIST_EXCEPTION, INCORRECT_PASSWORD_EXCEPTION, INCORRECT_USERNAME_EXCEPTION, KUBER_EXCEPTION, PROVIDER_EXCEPTION
# from app.constants.exceptions import ALREADY_REGISTERED_EXCEPTION, COOKIE_EXCEPTION, CREDENTIALS_EXCEPTION, DATABASE_EXCEPTION, GITHUB_OAUTH_EXCEPTION, GOOGLE_OAUTH_EXCEPTION, INCORRENT_PASSWORD_EXCEPTION, INCORRENT_USERNAME_EXCEPTION, KUBER_EXCEPTION, LOGIN_EXCEPTION, PROVIDER_EXCEPTION, SIGNUP_EXCEPTION, CustomException
from app.auth.jwt_handler import create_access_token, create_refresh_token, decodeJWT, set_cookie
from app.auth.password_handler import get_password_hash, verify_password
from app.controllers.db import add_blacklist_token, add_user_identity, create_signup_credit_for_user, add_user, get_user, get_user_by_id, get_user_identity_by_provider, is_token_blacklisted
from app.api.api import create_api_key

from app.models.users import UserinDB

from app.constants.token import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from app.auth.oauth import get_github_token, get_google_token, get_user_info_github, oauth, GITHUB_CLIENT_ID




router = APIRouter()

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
    try:
        provider = request.path_params['provider']
        user_info = None
        match provider:
            case "google":
                access_token = await get_google_token(request)
                user_email, provider_id, user_image  = access_token['userinfo']["email"] , access_token['userinfo']["sub"], access_token['userinfo']["picture"]
                data = UserinDB(
                    identifier = user_email,
                    email = user_email,
                    provider = provider,
                    provider_id = provider_id, 
                    image = user_image
                )

                user_info = access_token['userinfo']
                
            
            case "github":
                access_token = await get_github_token(request.query_params['code'])
                user_info = await get_user_info_github(access_token)
                provider_id, username, user_email, user_image  = user_info['id'], user_info["login"], user_info['email'], user_info["avatar_url"]
                data = UserinDB(
                    identifier = username,
                    email = user_email,
                    provider = provider,
                    provider_id = provider_id, 
                    image = user_image
                )

                user_info = user_info

            case _:
                raise PROVIDER_EXCEPTION
            
        user = await get_user(data) 

        if not user:
            id = await initialize_user(data, user_info)
        else:
            if user.provider != provider:
                user_identity = await get_user_identity_by_provider(user.id, provider)
                if not user_identity:
                    await add_user_identity(user.id, data, user_info)

            id = user.id

        local_token = create_access_token(data={"id": id})
        refresh_token = create_refresh_token(data={"id": id})
        id_and_tokens = (id, local_token, refresh_token)
        response = await get_user_profile(request, id_and_tokens)
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
        print(e)
        raise DATABASE_EXCEPTION
    
    except Exception as e:
        print(e)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail= "Exception in getting token"
        )

    
async def initialize_user( data, provider_data = None):
    id = await add_user(data, provider_data)
    await create_api_key("default", id)
    initial_credit = 20000
    await create_signup_credit_for_user( id, initial_credit, data.provider)
    return id 

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(request:Request, form : OAuth2PasswordRequestForm = Depends()):
    try:
        hashed_password = get_password_hash(form.password)
        data = UserinDB(**{"identifier": form.username, "provider": "password", "hashed_pw": hashed_password})
        
        user = await get_user(data)
        if user:
            raise ALREADY_REGISTERED_EXCEPTION
        
        id = await initialize_user(data, None)
        

        local_token = create_access_token(data={"id": id})
        refresh_token = create_refresh_token(data={"id": id})
        id_and_tokens = (id, local_token, refresh_token)
        response = await get_user_profile(request, id_and_tokens)
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
    try:
        data = UserinDB(**{"identifier": form.username, "provider": "password"})
        user = await get_user(data)
        if not user:
            raise INCORRECT_USERNAME_EXCEPTION
        
        id = user.id
        hashed_pw = user.hashed_pw

        if not verify_password(form.password, hashed_pw):
            raise INCORRECT_PASSWORD_EXCEPTION
        
        local_token = create_access_token(data={"id": id})
        refresh_token = create_refresh_token(data={"id": id})
        id_and_tokens = (id, local_token, refresh_token)
        response = await get_user_profile(request, id_and_tokens)

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


@router.get('/logout')
async def logout(request:Request, tokens: tuple = Depends(get_current_user_token)):
    try :
        _, refresh_token = tokens
        await add_blacklist_token(refresh_token)
        response = JSONResponse(content={"result": True}, status_code=200)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
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
async def get_user_profile(request:Request, id_and_tokens:tuple = Depends(get_current_user_id_http)):

    try:
        id, access_token, refresh_token = id_and_tokens

        data =await get_user_by_id(id)
        profile = {
            "identifier": data.identifier,
            "provider": data.provider,
            "email": data.email,
            "image": data.image
        }
        response = JSONResponse(content=profile, status_code=200)

        if access_token and refresh_token:
            set_cookie(response, access_token, refresh_token)

        return response
    
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

