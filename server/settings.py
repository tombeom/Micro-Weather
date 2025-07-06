from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_USERNAME: str
    MONGODB_PASSWORD: str
    MONGODB_URL: str

    @classmethod
    @lru_cache
    def get_settings(cls) -> "Settings":
        return cls()
