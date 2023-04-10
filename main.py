import sys
from fastapi import FastAPI, HTTPException
from app.api.users_api import router as users_router
from app.api.api import router as api_keys_router
from app.api.ws_proxy import router as ws_proxy_router

from starlette.middleware.sessions import SessionMiddleware
from decouple import config
import httpx
from fastapi.middleware.cors import CORSMiddleware

from app.db.prisma import prisma


SESSION_SECRET_KEY = config('SESSION_SECRET_KEY') or None
if SESSION_SECRET_KEY is None:
    raise 'Missing SESSION_SECRET_KEY'

CORS_DOMAINS= config('CORS_DOMAINS') or None
if CORS_DOMAINS is None:
    raise 'Missing CORS_DOMAINS'

CORS_DOMAINS = CORS_DOMAINS.split(',')

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_DOMAINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(users_router, prefix= "/auth")
app.include_router(api_keys_router, prefix = "/api/v1")
app.include_router(ws_proxy_router)



@app.on_event('startup')
async def startup_event():
    try:
        await prisma.connect()

    except Exception as e:
        print("Error during startup")
        sys.exit(1)
    


@app.on_event('shutdown')
async def shutdown_event():
    await prisma.disconnect()



