import os
from enum import Enum

import dotenv

envfile = "bot.env"
if os.path.exists(envfile):
    dotenv.load_dotenv(envfile)


class EnvVars(Enum):
    BOT_TOKEN = "BOT_TOKEN"
    REGISTRATION_PASSWORD = "REGISTRATION_PASSWORD"
    DEPLOY_METHOD = "DEPLOY_METHOD"
    DB_LOCATION = "DB_LOCATION"


def get_env(key: EnvVars) -> str:
    value = os.getenv(key.value)
    if not value:
        raise RuntimeError(f"Missing required env var: {key}")
    return value
