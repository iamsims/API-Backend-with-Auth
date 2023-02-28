from fastapi import FastAPI
from app.api.users_api import router as users_router

from starlette.middleware.sessions import SessionMiddleware
from decouple import config

SECRET_KEY = config('SECRET_KEY') or None
if SECRET_KEY is None:
    raise 'Missing SECRET_KEY'

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


app.include_router(users_router)

