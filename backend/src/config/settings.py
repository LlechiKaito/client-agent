import os

from dotenv import load_dotenv

load_dotenv()

IS_LAMBDA: bool = "AWS_LAMBDA_FUNCTION_NAME" in os.environ


def _require_env(key: str) -> str:
    value = os.environ.get(key)
    if value is None:
        raise RuntimeError(f"{key} is not set")
    return value


def _optional_env(key: str, default: str) -> str:
    value = os.environ.get(key)
    if value is not None:
        return value
    return default


APP_HOST: str = _optional_env("APP_HOST", "0.0.0.0") if IS_LAMBDA else _require_env("APP_HOST")
APP_PORT: int = int(_optional_env("APP_PORT", "8000") if IS_LAMBDA else _require_env("APP_PORT"))
APP_ENV: str = _require_env("APP_ENV")

LINE_CHANNEL_SECRET: str = _require_env("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN: str = _require_env("LINE_CHANNEL_ACCESS_TOKEN")

ANTHROPIC_API_KEY: str = _require_env("ANTHROPIC_API_KEY")

GAS_WEBAPP_URL: str = _require_env("GAS_WEBAPP_URL")

GAS_MAIL_WEBAPP_URL: str = _require_env("GAS_MAIL_WEBAPP_URL")
