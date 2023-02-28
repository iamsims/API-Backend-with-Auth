from enum import Enum
from typing import *

from fastapi import APIRouter, params, routing, Depends
from fastapi.datastructures import DefaultPlaceholder, Default
from fastapi.encoders import SetIntStr, DictIntStrAny
from fastapi.openapi.models import Response
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from loguru import logger
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute
from starlette.types import ASGIApp

from app.settings import configs

api_settings = configs.api_settings


class RequestWithLogger(Request):

    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            chunks = []
            async for chunk in self.stream():
                chunks.append(chunk)
            self._body = b"".join(chunks)

        if configs.is_development():
            logger.info(f"Request body : {self._body}")

        return self._body


class CustomAPIRoute(APIRoute):
    def __init__(
            self,
            path: str,
            endpoint: Callable[..., Any],
            *,
            response_model: Optional[Type[Any]] = None,
            status_code: Optional[int] = None,
            tags: Optional[List[Union[str, Enum]]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            response_description: str = "Successful Response",
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            deprecated: Optional[bool] = None,
            name: Optional[str] = None,
            methods: Optional[Union[Set[str], List[str]]] = None,
            operation_id: Optional[str] = None,
            response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            include_in_schema: bool = True,
            response_class: Union[Type[Response], DefaultPlaceholder] = Default(
                JSONResponse
            ),
            dependency_overrides_provider: Optional[Any] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            openapi_extra: Optional[Dict[str, Any]] = None,
            generate_unique_id_function: Callable[[APIRoute], str] = Default(
                generate_unique_id
            ),
    ):
        super().__init__(
            path,
            endpoint,
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses,
            deprecated=deprecated,
            name=name,
            methods=methods,
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=configs.exclude_none_in_all_response_models,
            include_in_schema=include_in_schema,
            response_class=response_class,
            dependency_overrides_provider=dependency_overrides_provider,
            callbacks=callbacks,
            openapi_extra=openapi_extra,
            generate_unique_id_function=generate_unique_id_function
        )

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def handler(request: Request) -> Response:
            request = RequestWithLogger(request.scope, request.receive)
            response = await original_route_handler(request)
            if configs.is_development():
                logger.info(f"Response body : {response.body if response.__dict__.get('body') else ''}")
            return response

        return handler


# Extend API Router to include custom API Route show that own customization
# can be done that applies to all routes
class CustomAPIRouter(APIRouter):

    def __init__(
            self,
            *,
            prefix: str,
            tags: Optional[List[Union[str, Enum]]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            default_response_class: Type[Response] = Default(JSONResponse),
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            routes: Optional[List[routing.BaseRoute]] = None,
            redirect_slashes: bool = True,
            default: Optional[ASGIApp] = None,
            dependency_overrides_provider: Optional[Any] = None,
            route_class: Type[APIRoute] = CustomAPIRoute,
            on_startup: Optional[Sequence[Callable[[], Any]]] = None,
            on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
            deprecated: Optional[bool] = None,
            include_in_schema: bool = True,
            generate_unique_id_function: Callable[[APIRoute], str] = Default(
                generate_unique_id
            ),
    ):
        super().__init__(
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            dependency_overrides_provider=dependency_overrides_provider,
            route_class=route_class,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function,
            prefix=api_settings.root_path + prefix
        )
