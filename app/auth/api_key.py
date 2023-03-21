from fastapi import HTTPException, status
import secrets
import base64

    
def generate_api_key():
    try:
        random_bytes = secrets.token_bytes(48)
        api_key = base64.b64encode(random_bytes).decode('utf-8')
        return api_key
    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in generating api key"
        )
    

