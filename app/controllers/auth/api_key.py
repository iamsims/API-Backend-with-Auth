from fastapi import HTTPException, status
from app.utils.random import generate_random_string
import base64
    
def generate_api_key():
    return generate_random_string()
        

def tobinary(api_key):
    try:
        return base64.b64decode(api_key)
    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in converting api key to binary"
        )


def tostring(api_key):
    try:
        return base64.b64encode(api_key)
    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in converting api key to string"
        )

