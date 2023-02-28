from pydantic import BaseSettings


class ApiSettings(BaseSettings):
    title: str = "[Kuber] Backend API"
    description: str = "Rest endpoints for better-collected forms integrator API"
    version: str = "1.0.0"
    allowed_origins: str = "http://localhost:3000,https://dev.bettercollected.io"
    root_path: str = "/"
    docs_path: str = "/docs"
    redoc_path: str = "/redoc"
    openapi_path: str = "/openapi.json"
    host: str = "http://localhost:8000"
    root_path_in_servers = False
    key_prefix: str = "better_collected_"
    key_id_length: int = 35
    key_password_length: int = 20
    jwt_secret: str = ""
    access_token_expiry_minutes: int = 60
    refresh_token_expiry_days: int = 30
    client_redirect_uri = "https://bettercollected.com"
    post_scheduler_url = "http://localhost:8001/api/v1"

    class Config:
        env_prefix = "API_"
