import datetime as dt
import enum
from typing import Any, Optional, Dict

from app.models.common.mongo_document import MongoDocument


class Provider(str, enum.Enum):
    GOOGLE = 'google'
    TYPEFORM = 'typeform'

    @classmethod
    def list_providers(cls):
        return [v.value for p, v in cls.__members__.items()]


class Oauth2CredentialDocument(MongoDocument):
    user_id: Optional[str]
    email: Optional[str]
    state: Optional[str]
    provider: Optional[Provider]
    credentials: Optional[Dict[str, Any]]
    created_at: Optional[dt.datetime]
    updated_at: Optional[dt.datetime]

    class Collection:
        name = "oauth2credentials"

    class Settings:
        bson_encoders = {
            dt.datetime: lambda o: dt.datetime.isoformat(o),
            dt.date: lambda o: dt.date.isoformat(o),
            dt.time: lambda o: dt.time.isoformat(o),
        }
