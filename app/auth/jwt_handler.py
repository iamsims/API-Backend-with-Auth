import time 
import jwt 
from decouple import config


JWT_SECRET = config('secret')
JWT_ALGORITHM = config('algorithm')


def token_response(token: str):
    return {
        'access_token': token
    }

def signJWT(user_id: int):
    payload = {
        'user_id': user_id,
        'expiry': time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decodeJWT(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return payload if payload["expiry"] > time.time() else None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

