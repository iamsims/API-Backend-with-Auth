from fastapi import FastAPI
from loguru import logger
from starlette.requests import Request
from starlette.responses import Response

from app.settings import configs


def init_middlewares(app: 'FastAPI'):
    @app.middleware('http')
    async def request_logger(request: 'Request', call_next):
        logger.info(f'Client Ip : {request.headers.get("X-Forwarded-For")}')
        logger.info(f"Request : Host {request.method} {request.url.path} {request.url.query}")
        response: Response = await call_next(request)

        try:
            if configs.is_development() and hasattr(response, 'body'):
                logger.info(f'Response: {response.status_code} {response.body}')
        except Exception as e:
            logger.error(f'Response Error: {e}')
            return response
        return response
