from enum import Enum
from pydantic import BaseSettings


class AppEnvTypes(Enum):
    prod: str = "prod"  # pyright: reportGeneralTypeIssues=false
    dev: str = "dev"  # pyright: reportGeneralTypeIssues=false
    test: str = "test"  # pyright: reportGeneralTypeIssues=false


class BaseAppSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes.prod

    class Config:
        env_file = ".env"
