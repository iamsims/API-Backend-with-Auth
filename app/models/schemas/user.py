import datetime as dt
import enum
from typing import Optional, List, Dict

from beanie import Indexed
from pydantic import BaseModel

from app.models.common.mongo_document import MongoDocument


class Roles(str, enum.Enum):
    ADMIN: str = "ADMIN"
    FORM_RESPONDER: str = "FORM_RESPONDER"
    FORM_CREATOR: str = "FORM_CREATOR"


class Services(BaseModel):
    provider: str
    status: str
    credentials: Dict[str, str]


class UserDocument(MongoDocument):
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    verified_email: Optional[bool]
    profile_picture: Optional[str]
    email: Indexed(str, unique=True)
    created_at: Optional[dt.datetime]
    updated_at: Optional[dt.datetime]
    services: Optional[List[Services]]

    class Collection:
        name = "users"

    class Settings:
        bson_encoders = {
            dt.datetime: lambda o: dt.datetime.isoformat(o),
            dt.date: lambda o: dt.date.isoformat(o),
            dt.time: lambda o: dt.time.isoformat(o),
        }
