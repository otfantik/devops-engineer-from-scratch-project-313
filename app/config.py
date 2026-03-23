from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    BASE_URL: str = "http://localhost:8080"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
