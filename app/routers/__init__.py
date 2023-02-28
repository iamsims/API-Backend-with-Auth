from fastapi import FastAPI

from app.routers import (
    google_router
)


def router_init(app: 'FastAPI'):
    app.include_router(
        google_router.router,
        tags=["Google"]
    )
