from fastapi import FastAPI, HTTPException
from app.api.users_api import router as users_router

from starlette.middleware.sessions import SessionMiddleware
from decouple import config
import httpx


SECRET_KEY = config('SECRET_KEY') or None
if SECRET_KEY is None:
    raise 'Missing SECRET_KEY'

KUBER_SERVER = config('KUBER_SERVER') or None
if KUBER_SERVER is None:
    raise 'Missing KUBER_SERVER'

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(users_router)

@app.on_event('startup')
async def startup_event():
    client = httpx.AsyncClient(base_url=KUBER_SERVER)  # this is the other server
    app.state.client = client


@app.on_event('shutdown')
async def shutdown_event():
    client = app.state.client
    await client.aclose()

