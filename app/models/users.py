from pydantic import BaseModel
from typing import Union

class UserinDB(BaseModel):
    identifier : str
    email: Union[str, None] = None
    hashed_pw: Union[str, None] = None
    provider: str
    provider_id: Union[str, None] = None
    api_key: Union[str, None] = None


class UserLoginSchema(BaseModel):
    username : str
    password : Union[str, None] = None
