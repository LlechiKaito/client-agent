import os

from dotenv import load_dotenv

load_dotenv()


def _require_env(key: str) -> str:
    value = os.environ.get(key)
    if value is None:
        raise RuntimeError(f"{key} is not set")
    return value


APP_HOST: str = _require_env("APP_HOST")
APP_PORT: int = int(_require_env("APP_PORT"))
APP_ENV: str = _require_env("APP_ENV")
FRONTEND_URL: str = _require_env("FRONTEND_URL")
