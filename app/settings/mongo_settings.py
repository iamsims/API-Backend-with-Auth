from pydantic import BaseSettings


class MongoSettings(BaseSettings):
    db: str = "kuber_api"
    uri: str = ""

    class Config:
        env_prefix = "MONGO_"
