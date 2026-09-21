from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    CACHE_URL: str
    SECRET: str
    HASH: str = "HS256"
    TOKEN_EXPIRE_HOURS: int = 3
    REGISTER_SESSION_TTL: int = 600
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    COOKIE_DOMAIN: str | None = None
    COOKIE_SECURE: bool = False
    BE_URL: str = "http://localhost:8000"

    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_USE_TLS: bool = True
    SMTP_FROM: EmailStr | None = None
    SMTP_FROM_NAME: str = "ITS Test API"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url(self) -> str:
        url = self.DATABASE_URL
        return "postgresql+asyncpg://" + url.split("://", 1)[1]


settings = Settings()
