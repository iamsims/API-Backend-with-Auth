from typing import Optional, List

from beanie import PydanticObjectId
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

UserIdentifier = str


class UserLoginWithOTP(BaseModel):
    email: EmailStr
    otp_code: str


class User(BaseModel):
    id: str | PydanticObjectId
    sub: UserIdentifier
    username: Optional[str] = Field()
    roles: Optional[List[str]] = []
    services: Optional[List[str]] = []

    def is_admin(self):
        return "ADMIN" in self.roles

    def is_not_admin(self):
        return not self.is_admin()


class AuthenticationStatus(BaseModel):
    user: User = Field()
