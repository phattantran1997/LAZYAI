from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGO_URI: str  
    PROJECT_NAME: str = "LAZYAI"
    ALLOWED_HOSTS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings(MONGO_URI="mongodb://localhost:27017/mydb")  