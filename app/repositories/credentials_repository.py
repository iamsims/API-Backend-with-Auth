import enum
import json
from datetime import datetime
from typing import List

from app.models.schemas.credentials import Oauth2CredentialDocument, Provider


async def get_credential(email: str, provider: Provider):
    return await Oauth2CredentialDocument.find_one({"email": email, "provider": provider})


# Get all credentials associated with email
async def get_all_credentials(email: str) -> List[Oauth2CredentialDocument]:
    return await Oauth2CredentialDocument.find_many({"email": email}).to_list()


async def save_credentials(email, credentials, state, provider):
    exists = await get_credential(email=email, provider=provider)
    if exists and exists.email == email and exists.provider == provider:
        oauth2credential_document = exists
        oauth2credential_document.created_at = exists.created_at
    else:
        oauth2credential_document = Oauth2CredentialDocument()
        oauth2credential_document.created_at = datetime.utcnow()
    oauth2credential_document.email = email
    oauth2credential_document.provider = provider
    oauth2credential_document.state = state
    oauth2credential_document.credentials = credentials
    oauth2credential_document.updated_at = datetime.utcnow()
    await oauth2credential_document.save()


async def revoke_credentials(email: str, provider: Provider):
    exists = await get_credential(email=email, provider=provider)
    if exists:
        return await exists.delete()
    return None
