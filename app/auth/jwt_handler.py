from typing import Union
from jose import jwt 
from datetime import datetime, timedelta
from decouple import config
# from typing import Union
import time
from fastapi import HTTPException, status


JWT_SECRET = config('secret')
JWT_ALGORITHM = config('algorithm')
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30


CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

ALREADY_REGISTERED_EXCEPTION = HTTPException(
    status_code=400, 
    detail="Username already registered"
    )

DATABASE_EXCEPTION = HTTPException(
    status_code=500,
    detail="Database error"
)

INCORRENT_USERNAME_EXCEPTION = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
        )

INCORRENT_PASSWORD_EXCEPTION = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password ",
        )
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta

    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    # print(to_encode)
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt



def create_refresh_token(data):
    expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    return create_access_token(data=data, expires_delta=expires)


def decodeJWT(token: str):
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    # print(payload)
    return payload if payload["exp"] > time.time() else None

def verify_jwt(jwtoken : str):
    isTokenValid : bool = False 
    payload = decodeJWT(jwtoken)
    if payload:
        isTokenValid = True
    return isTokenValid
