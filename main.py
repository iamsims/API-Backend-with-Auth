from fastapi import FastAPI
from app.api.users_api import router as users_router

from starlette.middleware.sessions import SessionMiddleware
from decouple import config
import httpx

SECRET_KEY = config('SECRET_KEY') or None
if SECRET_KEY is None:
    raise 'Missing SECRET_KEY'

KUBER_SERVER = config('KUBER_SERVER') or None
if KUBER_SERVER is None:
    raise 'Missing KUBER_SERVER'

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


app.include_router(users_router)

@app.on_event('startup')
async def startup_event():
    client = httpx.AsyncClient(base_url=KUBER_SERVER)  # this is the other server
    app.state.client = client


@app.on_event('shutdown')
async def shutdown_event():
    client = app.state.client
    await client.aclose()


# from fastapi import FastAPI, Request
# from fastapi.responses import StreamingResponse
# from starlette.background import BackgroundTask
# import httpx

# app = FastAPI()

# @app.on_event('startup')
# async def startup_event():
#     client = httpx.AsyncClient(base_url='http://127.0.0.1:8001/')  # this is the other server
#     app.state.client = client


# @app.on_event('shutdown')
# async def shutdown_event():
#     client = app.state.client
#     await client.aclose()


# async def _reverse_proxy(request: Request):
#     client = request.app.state.client
#     url = httpx.URL(path=request.url.path, query=request.url.query.encode('utf-8'))
#     req = client.build_request(
#         request.method, url, headers=request.headers.raw, content=request.stream()
#     )
#     r = await client.send(req, stream=True)
#     return StreamingResponse(
#         r.aiter_raw(),
#         status_code=r.status_code,
#         headers=r.headers,
#         background=BackgroundTask(r.aclose)
#     )


# app.add_route('/upload/{path:path}', _reverse_proxy, ['POST'])


# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app, host='0.0.0.0', port=8000)

