import datetime

from starlette.middleware.cors import CORSMiddleware

from app.models.schemas.allowed_origins import AllowedOriginsDocument
from app.utils.async_utils import asyncio_run


class DynamicCORSMiddleware(CORSMiddleware):
    allowedOrigins = []
    time = datetime.datetime.utcnow()

    def is_allowed_origin(self, origin: str) -> bool:
        if datetime.datetime.utcnow().timestamp() < (
                self.time.timestamp() + float(60 * 60)) and origin in self.allowedOrigins:
            return True
        origins = asyncio_run(AllowedOriginsDocument.find().to_list())
        all_origins = [o.origin for o in origins]
        self.allowedOrigins = [*all_origins]
        allow = origin in all_origins
        self.time = datetime.datetime.utcnow()
        return allow
