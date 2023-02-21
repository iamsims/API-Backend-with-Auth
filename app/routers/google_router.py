from fastapi import APIRouter
from fastapi import Request, Depends
from starlette.responses import RedirectResponse, Response

from app.models.dtos.auth import User
from app.services import google_service
from app.services.auth_service import set_tokens_to_response, get_logged_user

router = APIRouter(prefix="/api/v1/auth/google")


@router.get("/oauth")
def _authenticate_google(request: Request):
    client_referer_url = request.headers.get('referer')
    authorization_url = google_service.authenticate_google(client_referer_url)
    return RedirectResponse(authorization_url)


@router.get("/basicAuthCallback")
async def _basic_auth_callback(request: Request, response: Response):
    client_referer_url, token_user = await google_service.basic_auth_callback(request)
    set_tokens_to_response(user=User(**token_user, sub=token_user['email']),
                           response=response)


@router.get('/whoami')
async def _get_state_of_user(request: Request, user: 'User' = Depends(get_logged_user)):
    return user.sub
