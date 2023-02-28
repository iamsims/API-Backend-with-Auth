import datetime as dt
from typing import Optional, List, Dict, Any

from pydantic import BaseModel

from app.models.common.mongo_document import MongoDocument
from app.models.dtos.google_forms import GoogleFormResponseDto
from app.models.schemas.credentials import Provider


# As response is tied with form_id provider is redundant information here
# TODO Refactor this in new repo
class GoogleFormResponseDocument(MongoDocument, GoogleFormResponseDto):
    dataOwnerFields: Optional[List[Dict[str, str | None]]] = []
    dataOwnerIdentifier: Optional[str]
    provider: Provider = Provider.GOOGLE
    formId: Optional[str]

    class Collection:
        name = "formResponses"

    class Settings:
        bson_encoders = {
            dt.datetime: lambda o: dt.datetime.isoformat(o),
            dt.date: lambda o: dt.date.isoformat(o),
            dt.time: lambda o: dt.time.isoformat(o),
        }


# Generic class that represents forms collection for now Need to refactor later in new repo
class FormResponseDocument(MongoDocument):
    formId: str
    provider: Provider

    class Collection:
        name = "formResponses"

    class Settings:
        bson_encoders = {
            dt.datetime: lambda o: dt.datetime.isoformat(o),
            dt.date: lambda o: dt.date.isoformat(o),
            dt.time: lambda o: dt.time.isoformat(o),
        }


class TypeFormResponseDocument(MongoDocument):
    responseId: str
    formId: str
    response_data: Dict[str, Any]
    provider: Provider = Provider.TYPEFORM
    dataOwnerIdentifier: Optional[str]

    class Collection:
        name = "formResponses"

    class Settings:
        bson_encoders = {
            dt.datetime: lambda o: dt.datetime.isoformat(o),
            dt.date: lambda o: dt.date.isoformat(o),
            dt.time: lambda o: dt.time.isoformat(o),
        }
