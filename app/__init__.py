from fastapi import FastAPI
from app.handlers.cors_handler import init_cors
from app.handlers.exception_handler import init_exception_handlers
from app.handlers.request_handler import init_middlewares
from app.handlers.swagger_handler import init_swagger
from app.repositories import init_db, close_db
from app.routers import router_init
from app.settings import configs


def init_app(app: 'FastAPI'):
    app.add_event_handler("startup",init_db)
    app.add_event_handler("shutdown",close_db)
    init_middlewares(app)
    init_exception_handlers(app)
    init_cors(app)
    router_init(app)
    init_swagger(app)
