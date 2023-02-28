import asyncio

from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import InvalidOperation

from app.models.schemas.credentials import Oauth2CredentialDocument
from app.models.schemas.user import UserDocument
from app.settings import configs

mongo_settings = configs.mongo_settings
_client = AsyncIOMotorClient(mongo_settings.uri)


async def init_db():
    _client.get_io_loop = asyncio.get_running_loop
    db = _client[mongo_settings.db]
    await init_beanie(database=db,
                      document_models=[UserDocument, Oauth2CredentialDocument])
    logger.info("Database connected successfully.")


async def close_db():
    try:
        _client.close()
        logger.info("Database disconnected successfully.")
    except InvalidOperation as error:
        logger.error("Database disconnect failure.")
        logger.error(error)
