from typing import List

from beanie import PydanticObjectId
from bson import ObjectId
from fastapi import HTTPException
from pymongo.results import UpdateResult

from app.models.schemas.user import UserDocument


class UserRepository:
    @staticmethod
    async def get_user_by_id(user_id: PydanticObjectId):
        user_document = await UserDocument.find_one({"_id": ObjectId(user_id)})
        if not user_document:
            raise HTTPException(404, "User not found")
        return user_document

    @staticmethod
    async def add_roles_to_user(user_id: PydanticObjectId, roles: List[str]):
        user_document = await UserDocument.find_one({"_id": user_id}).update({"$addToSet": {"roles": {"$each": roles}}})
        if not user_document.matched_count > 0:
            raise HTTPException(404, "User not found")
        return f"Add roles to user success."

    @staticmethod
    async def remove_roles_form_user(user_id: PydanticObjectId, roles: List[str]):
        user_document = await UserDocument.find_one({"_id": user_id}).update({"$pull": {"roles": {"$in": roles}}})
        if not user_document.matched_count > 0:
            raise HTTPException(404, "User not found")
        return f"Removes roles of user success"
