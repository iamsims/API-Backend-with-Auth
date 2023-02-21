from typing import Optional, List

from beanie import PydanticObjectId
from pydantic import BaseModel


class UserPatchRequest(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]


class UserResponseDto(BaseModel):
    id: PydanticObjectId
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    email: str
    roles: List[str] = ["FORM_RESPONDER"]
    services: Optional[List[str]]
