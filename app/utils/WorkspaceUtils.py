from beanie import PydanticObjectId
from fastapi import HTTPException

from app.models.dtos.auth import User
from app.models.schemas.credentials import Provider
from app.models.schemas.workspace_users import WorkspaceUsers
from app.services.impl.google_form_transformer_service import GoogleFormTransformerService
from app.services.impl.typeform_form_transformer_service import TypeFormTransformerService


async def check_user_is_admin_in_workspace(workspace_id: PydanticObjectId, user: User) -> bool:
    if not user or not workspace_id:
        return False
    workspace_user = await WorkspaceUsers.find_one(
        {"workspaceId": PydanticObjectId(workspace_id), "userId": PydanticObjectId(user.id)})
    return True if workspace_user else False


def check_if_valid_url_in_workspace_policies(url: str):
    import re
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def get_transformer_for_provider(provider: str | Provider):
    match provider:
        case Provider.GOOGLE:
            return GoogleFormTransformerService()
        case Provider.TYPEFORM:
            return TypeFormTransformerService()
        case _:
            raise HTTPException(status_code=400,
                                detail=f"Unknown provider. Please use one of the following {Provider.list_providers()}")
