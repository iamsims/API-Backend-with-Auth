import loguru
from fastapi import FastAPI, HTTPException
from google.auth.exceptions import TransportError
from jose import ExpiredSignatureError, JWTError
from starlette.responses import JSONResponse

from app.exceptions.forbidden_exception import ForbiddenException
from app.exceptions.not_found_exception import NotFoundException


def init_exception_handlers(app: 'FastAPI'):
    @app.exception_handler(KeyError)
    async def key_error_handler(request, exc):
        loguru.logger.error(exc)
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": "Error while parsing data in request."}
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        loguru.logger.error(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": exc.detail}
        )

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request, exc):
        loguru.logger.error(exc.message)
        return JSONResponse(
            status_code=404,
            content={"code": 404, "message": exc.message}
        )

    @app.exception_handler(NotImplementedError)
    async def not_implemented_exception_handler(request, exc):
        loguru.logger.error(exc)
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": exc}
        )

    @app.exception_handler(ExpiredSignatureError)
    async def expired_signature_exception_handler(request, exc):
        loguru.logger.error(str(exc))
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": "Error token expired."}
        )

    @app.exception_handler(ForbiddenException)
    async def forbidden_exception_handler(request, exc: ForbiddenException):
        loguru.logger.error(exc.message)
        return JSONResponse(
            status_code=403,
            content={"code": 403, "message": exc.message}
        )

    @app.exception_handler(TransportError)
    async def google_transport_error(request, exc: TransportError):
        loguru.logger.error(str(exc))
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": "Unable to find the server at oauth2.googleapis.com"}
        )

    @app.exception_handler(JWTError)
    async def jwt_exception_handler(request, exc: JWTError):
        loguru.logger.error(exc)
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": str(exc)}
        )
