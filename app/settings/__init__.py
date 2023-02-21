from functools import lru_cache

from pydantic import BaseSettings

from app.settings.api_settings import ApiSettings
from app.settings.mongo_settings import MongoSettings
from app.settings.google_settings import GoogleSettings



__all__ = "configs"


class Settings(BaseSettings):
    environment: str = "development"
    exclude_none_in_all_response_models: bool = True

    organization_name: str = "Kuber"

    api_settings: ApiSettings = ApiSettings()
    mongo_settings: MongoSettings = MongoSettings()
    google_settings: GoogleSettings = GoogleSettings()


    def is_development(self):
        return self.environment == "development"


@lru_cache()
def get_configs():
    return Settings()


configs = get_configs()
