import os

from fastapi import FastAPI
from dotenv import load_dotenv
from app import init_app
from app.settings import configs

api_settings = configs.api_settings

load_dotenv(dotenv_path=os.getenv("DOTENV_PATH", '.env.example'))

app = FastAPI(
    title=api_settings.title,
    description=api_settings.description,
    version=api_settings.version,
    # root_path='/api/v1',
    # docs_url="/api/v1/openapi.json",
    redoc_url=None
)

init_app(app)
