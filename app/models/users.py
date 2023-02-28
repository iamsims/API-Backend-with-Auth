from pydantic import BaseModel
from typing import Union

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

# class User(BaseModel):
#     username: str
#     email: Union[str, None] = None
#     disabled: Union[bool, None] = None


# class UserInDB(User):
#     hashed_password: str
    
class UserinDB(BaseModel):
    identifier : str
    hashed_pw: Union[str, None] = None
    provider: str
    provider_id: Union[str, None] = None


class UserLoginSchema(BaseModel):
    username : str
    password : Union[str, None] = None