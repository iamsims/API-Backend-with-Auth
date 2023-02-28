from beanie import PydanticObjectId

from app.models.dtos.auth import User
from app.repositories.user_repository import UserRepository


class UserService:
    @staticmethod
    async def get_user_by_id(user_id: PydanticObjectId):
        user = await UserRepository.get_user_by_id(user_id)
        user.id = str(user.id)
        return User(**user.dict(), sub=user.email)
