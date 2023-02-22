from jose import jwt 
from datetime import datetime, timedelta
from decouple import config
from typing import Union
import time


JWT_SECRET = config('secret')
JWT_ALGORITHM = config('algorithm')


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    print(to_encode)
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decodeJWT(token: str):
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload if payload["exp"] > time.time() else None

def verify_jwt(jwtoken : str):
    isTokenValid : bool = False 
    payload = decodeJWT(jwtoken)
    if payload:
        isTokenValid = True
    return isTokenValid
