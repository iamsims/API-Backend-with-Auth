import sys
from fastapi import FastAPI, HTTPException
from app.api.users_api import router as users_router
from app.api.api_keys import router as api_keys_router
from app.api.credit import router as credit_router
from app.api.proxy import router as proxy_router


from starlette.middleware.sessions import SessionMiddleware
from decouple import config
import httpx

from app.controllers.db import startup_db


SESSION_SECRET_KEY = config('SESSION_SECRET_KEY') or None
if SESSION_SECRET_KEY is None:
    raise 'Missing SESSION_SECRET_KEY'

KUBER_SERVER = config('KUBER_SERVER') or None
if KUBER_SERVER is None:
    raise 'Missing KUBER_SERVER'

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

app.include_router(users_router, prefix= "/auth")
app.include_router(api_keys_router, prefix = "/api")
app.include_router(credit_router, prefix = "/credit")
app.include_router(proxy_router)

@app.on_event('startup')
async def startup_event():
    try:
        engine = startup_db()
        app.state.engine = engine

    except Exception as e:
        print("Error during startup")
        sys.exit(1)
    
    client = httpx.AsyncClient(base_url=KUBER_SERVER)  # this is the other server
    app.state.client = client


@app.on_event('shutdown')
async def shutdown_event():
    client = app.state.client
    await client.aclose()


