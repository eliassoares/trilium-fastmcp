from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 6969
    trilium_token: str | None = None
    trilium_url: str | None = None

    updating_disabled: bool = True


settings = Settings()
