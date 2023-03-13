from app.models.users import UserinDB
from fastapi import HTTPException, status
from app.controllers.db import get_user
import secrets


async def get_api_key(data : UserinDB):
    try:
        # TODO: check if user is in db
        # user = await get_user(data)
        # if user.api_key:
            # return user.api_key
        
        api_key = generate_api_key()
        # data.api_key = api_key

        #TODO: update in user db
        # await update_user(data)
        return api_key
        
    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in getting api key for user"
        )
    
def generate_api_key():
    try:
        return secrets.token_hex(16)
    except:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Exception in generating api shhssh key"
        )
    

