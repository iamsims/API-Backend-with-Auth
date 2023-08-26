from fastapi import HTTPException, status, Request
from starlette.responses import JSONResponse
from app.constants.exceptions import (
    PROVIDER_EXCEPTION, CREDENTIALS_EXCEPTION, NOT_AUTHORIZED_EXCEPTION, DOESNT_EXIST_EXCEPTION, 
    SIGNUP_EXCEPTION, LOGIN_EXCEPTION, COOKIE_EXCEPTION, ENDPOINT_DOES_NOT_EXIST_EXCEPTION,
    CREDIT_NOT_ENOUGH_EXCEPTION, ALREADY_REGISTERED_EXCEPTION, DATABASE_DOWN_EXCEPTION, DATABASE_EXCEPTION, 
    INCORRECT_PASSWORD_EXCEPTION, INCORRECT_USERNAME_EXCEPTION
    )

def install_exception_handlers(app):

    @app.exception_handler(Exception)  # Catch-all handler
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500, 
            content={"message": "An error occurred"},
        )
    
    @app.exception_handler(PROVIDER_EXCEPTION)
    async def provider_exception_handler(
        request: Request, exc: PROVIDER_EXCEPTION
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    

    @app.exception_handler(CREDENTIALS_EXCEPTION)
    async def credentials_exception_handler(
        request: Request, exc: CREDENTIALS_EXCEPTION
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    

    @app.exception_handler(NOT_AUTHORIZED_EXCEPTION)
    async def not_authorized_exception_handler(
        request: Request, exc: NOT_AUTHORIZED_EXCEPTION
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    

    @app.exception_handler(DOESNT_EXIST_EXCEPTION)
    async def doesnt_exist_exception_handler(
        request: Request, exc: DOESNT_EXIST_EXCEPTION
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    

    @app.exception_handler(SIGNUP_EXCEPTION)
    async def signup_exception_handler(
        request: Request, exc: SIGNUP_EXCEPTION
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    

    @app.exception_handler(LOGIN_EXCEPTION)
    async def login_exception_handler(
        request: Request, exc: LOGIN_EXCEPTION
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    
    @app.exception_handler(ENDPOINT_DOES_NOT_EXIST_EXCEPTION)
    async def endpoint_does_not_exist_exception_handler(
        request: Request, exc: ENDPOINT_DOES_NOT_EXIST_EXCEPTION
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    @app.exception_handler(DATABASE_DOWN_EXCEPTION)
    async def database_down_exception_handler(
        request: Request, exc: DATABASE_DOWN_EXCEPTION
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    @app.exception_handler(INCORRECT_PASSWORD_EXCEPTION)
    async def incorrect_password_exception_handler(
        request: Request, exc: INCORRECT_PASSWORD_EXCEPTION
    ):
       return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    
    @app.exception_handler(INCORRECT_USERNAME_EXCEPTION)
    async def incorrect_username_exception_handler(
        request: Request, exc: INCORRECT_USERNAME_EXCEPTION
    ):
       return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    @app.exception_handler(CREDIT_NOT_ENOUGH_EXCEPTION)
    async def credit_not_enough_exception_handler(
        request: Request, exc: CREDIT_NOT_ENOUGH_EXCEPTION
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    

    @app.exception_handler(ALREADY_REGISTERED_EXCEPTION)
    async def already_registered_exception_handler(
        request: Request, exc: ALREADY_REGISTERED_EXCEPTION
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    

    @app.exception_handler(COOKIE_EXCEPTION)
    async def cookie_exception_handler(request: Request, exc: COOKIE_EXCEPTION):
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content={"message": exc.detail},
        )

    @app.exception_handler(DATABASE_EXCEPTION)
    async def database_exception_handler(request: Request, exc: DATABASE_EXCEPTION):
        print(exc,exc.args)
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    


