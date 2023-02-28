from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

from app.settings import configs

api_settings = configs.api_settings


def init_swagger(app):
    @app.get("/docs", include_in_schema=False)
    async def swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=f"{api_settings.host}/openapi.json",
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        )

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=f"{api_settings.host}/openapi.json",
            title=app.title + " - Swagger UI",
        )
