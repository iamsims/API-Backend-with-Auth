from fastapi import HTTPException, status
import secrets

    
def generate_api_key():
    try:
        api_key = secrets.token_hex(16) 
        return api_key
    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in generating api key"
        )
    

