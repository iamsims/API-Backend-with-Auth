from fastapi import FastAPI
from app.settings import configs
from fastapi.middleware.cors import CORSMiddleware


def init_cors(app: 'FastAPI'):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
