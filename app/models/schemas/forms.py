import datetime as dt
from typing import List, Optional, Dict, Any

from app.models.common.mongo_document import MongoDocument
from app.models.dtos.google_forms import GoogleFormDto
from app.models.schemas.credentials import Provider


class GoogleFormDocument(MongoDocument, GoogleFormDto):
    provider: Provider = Provider.GOOGLE
    dataOwnerFields: Optional[List[str]] = []

    class Collection:
        name = "forms"

    class Settings:
        bson_encoders = {
            dt.datetime: lambda o: dt.datetime.isoformat(o),
            dt.date: lambda o: dt.date.isoformat(o),
            dt.time: lambda o: dt.time.isoformat(o),
        }


# Generic class that represents forms collection for now Need to refactor later in new repo
class FormDocument(MongoDocument):
    provider: Provider

    class Collection:
        name = "forms"

    class Settings:
        bson_encoders = {
            dt.datetime: lambda o: dt.datetime.isoformat(o),
            dt.date: lambda o: dt.date.isoformat(o),
            dt.time: lambda o: dt.time.isoformat(o),
        }


class TypeFormDocument(MongoDocument):
    info: Dict[str, Any]
    formId: str
    dataOwnerFields: Optional[List[str]] = []
    provider: Provider = Provider.TYPEFORM

    class Collection:
        name = "forms"

    class Settings:
        bson_encoders = {
            dt.datetime: lambda o: dt.datetime.isoformat(o),
            dt.date: lambda o: dt.date.isoformat(o),
            dt.time: lambda o: dt.time.isoformat(o),
        }
