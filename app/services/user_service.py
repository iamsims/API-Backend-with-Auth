from typing import List

from beanie import PydanticObjectId
from fastapi import HTTPException

from app.models.dtos.auth import User
from app.models.dtos.user import UserPatchRequest, UserResponseDto
from app.models.schemas.user import UserDocument
from app.repositories.user_repository import UserRepository


class UserService:
    @staticmethod
    async def get_user_by_id(user_id: PydanticObjectId):
        user = await UserRepository.get_user_by_id(user_id)
        user.id = str(user.id)
        return User(**user.dict(), sub=user.email)

    # @staticmethod
    # async def add_roles_to_user(user_id: PydanticObjectId, roles: List[str]):
    #     return await UserRepository.add_roles_to_user(user_id, roles)
    #
    # @staticmethod
    # async def remove_roles_form_user(user_id: PydanticObjectId, roles: List[str]):
    #     return await UserRepository.remove_roles_form_user(user_id, roles)

    @staticmethod
    async def patch_user(user_id: PydanticObjectId, user_patch: UserPatchRequest, user: User):
        if not user.id == user_id or not user.is_admin():
            raise HTTPException(403, "You are not authorized to perform this action.")
        user_document = await UserDocument.find_one({"_id": user_id})
        user_document.first_name = user_patch.first_name if user_patch.first_name else user_document.first_name
        user_document.last_name = user_patch.last_name if user_patch.last_name else user_document.last_name
        user_document.username = user_patch.username if user_patch.username else user_document.username
        user = await user_document.save()
        return UserResponseDto(**user.dict())
