import subprocess
import sys, os
from fastapi import FastAPI
from app.api.auth import router as users_router
from app.api.api_key import router as api_router

from starlette.middleware.sessions import SessionMiddleware
from decouple import config
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.exception_handler import install_exception_handlers

from app.db.prisma import prisma

SESSION_SECRET_KEY = None
CORS_DOMAINS = None

try:
    SESSION_SECRET_KEY = config('SESSION_SECRET_KEY')
    CORS_DOMAINS= config('CORS_DOMAINS')
    CORS_DOMAINS = CORS_DOMAINS.split(',')

except:
    if SESSION_SECRET_KEY is None:
        raise 'Missing SESSION_SECRET_KEY'

    if CORS_DOMAINS is None:
        raise 'Missing CORS_DOMAINS'


app = FastAPI()

install_exception_handlers(app)

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_DOMAINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(users_router, prefix= "/auth")
app.include_router(api_router, prefix = "/api/v1")

@app.on_event('startup')
async def startup_event():
    try:
        env_vars = os.environ.copy()
        env_vars['DB_URL'] = prisma._datasource['url']
        subprocess.run(["prisma",'migrate','deploy'],env=env_vars)
        await prisma.connect()

    except Exception as e:
        print("Error during startup")
        sys.exit(1)


@app.on_event('shutdown')
async def shutdown_event():
    await prisma.disconnect()




