from app.models.common.mongo_document import MongoDocument


class AllowedOriginsDocument(MongoDocument):
    origin: str

    class Collection:
        name = "allowedOrigins"
