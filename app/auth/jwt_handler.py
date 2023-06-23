from typing import Union
from jose import jwt 
from datetime import datetime, timedelta
from decouple import config
import time
from app.constants.token import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
import uuid

JWT_ALGORITHM= None
JWT_SECRET = None 

try:
    JWT_SECRET = config('JWT_SECRET')
    JWT_ALGORITHM = config('JWT_ALGORITHM')

except:
    if JWT_SECRET is None:
        raise BaseException('Missing env variables for JWT_SECRET')
    if JWT_ALGORITHM is None:
        raise BaseException('Missing env variables for JWT_ALGORITHM')
    



def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta

    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    to_encode.update({"jti": str(uuid.uuid4())})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt



def create_refresh_token(data : dict):
    expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    return create_access_token(data=data, expires_delta=expires)


def decodeJWT(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    
    except Exception as e:
        print(e)
        return None

def verify_jwt(jwtoken : str):
    isTokenValid : bool = False 
    payload = decodeJWT(jwtoken)
    if payload:
        isTokenValid = True
    return isTokenValid


def set_cookie(response: dict, access_token: str, refresh_token : str):
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure= True, samesite="none", expires=ACCESS_TOKEN_EXPIRE_MINUTES*60)
    response.set_cookie(key= "refresh_token", value=refresh_token, httponly=True, secure= True, samesite="none", expires=REFRESH_TOKEN_EXPIRE_MINUTES*60)