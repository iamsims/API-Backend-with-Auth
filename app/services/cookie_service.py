import http.cookies

from starlette.responses import Response

from app.constants import app_constants
from app.settings import configs

api_settings = configs.api_settings


def set_cookie(
        response: Response,
        key: str,
        value: str = "",
        max_age: int = None,
        expires: int = None,
        path: str = "/",
        domain: str = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: str = "lax",
) -> None:
    cookie: http.cookies.BaseCookie = http.cookies.SimpleCookie()
    cookie[key] = value
    if max_age is not None:
        cookie[key]["max-age"] = max_age
    if expires is not None:
        cookie[key]["expires"] = expires
    if path is not None:
        cookie[key]["path"] = path
    if domain is not None:
        cookie[key]["domain"] = domain
    if secure:
        cookie[key]["secure"] = True
    if httponly:
        cookie[key]["httponly"] = True
    if samesite is not None:
        assert samesite.lower() in [
            "strict",
            "lax",
            "none",
        ], "samesite must be either 'strict', 'lax' or 'none'"
        cookie[key]["samesite"] = samesite
    cookie_val = cookie.output(header="").strip()
    response.raw_headers.append((b"set-cookie", cookie_val.encode("latin-1")))


def delete_cookie(
        response: Response,
        key: str,
        path: str = "/",
        domain: str = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: str = "lax",
) -> None:
    response.set_cookie(
        key,
        max_age=0,
        expires=0,
        path=path,
        domain=domain,
        secure=secure,
        httponly=httponly,
        samesite=samesite,
    )


def set_token_cookie(response: Response, key: str, token: str):
    should_be_secure = False if "localhost" in api_settings.host else True
    same_site = "none" if should_be_secure else "lax"
    set_cookie(
        response=response,
        key=key,
        value=token,
        httponly=True,
        secure=should_be_secure,
        # TODO prevent against csrf with same site after fix
        samesite=same_site,
        max_age=configs.api_settings.refresh_token_expiry_days * 24 * 60 * 60
    )


def delete_token_cookie(response: Response):
    should_be_secure = False if "localhost" in api_settings.host else True
    same_site = "none" if should_be_secure else "lax"
    delete_cookie(
        response=response,
        key=app_constants.authorization,
        httponly=True,
        secure=should_be_secure,
        # TODO prevent against csrf with same site after fix
        samesite=same_site
    )
    delete_cookie(
        response=response,
        key=app_constants.refresh_token,
        httponly=True,
        secure=should_be_secure,
        # TODO prevent against csrf with same site after fix
        samesite=same_site
    )
