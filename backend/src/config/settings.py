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


def _get_ssm_parameters(prefix: str, keys: list[str]) -> dict[str, str]:
    import boto3

    ssm = boto3.client("ssm")
    names = [f"{prefix}{key}" for key in keys]
    response = ssm.get_parameters(Names=names, WithDecryption=True)

    result: dict[str, str] = {}
    for param in response["Parameters"]:
        key = param["Name"].removeprefix(prefix)
        result[key] = param["Value"]

    missing = [key for key in keys if key not in result]
    if missing:
        raise RuntimeError(f"SSM parameters not found: {missing}")

    return result


APP_HOST: str = _optional_env("APP_HOST", "0.0.0.0") if IS_LAMBDA else _require_env("APP_HOST")
APP_PORT: int = int(_optional_env("APP_PORT", "8000") if IS_LAMBDA else _require_env("APP_PORT"))
APP_ENV: str = _require_env("APP_ENV")

_SSM_KEYS = [
    "LINE_CHANNEL_SECRET",
    "LINE_CHANNEL_ACCESS_TOKEN",
    "ANTHROPIC_API_KEY",
    "GAS_WEBAPP_URL",
    "GAS_MAIL_WEBAPP_URL",
]

if IS_LAMBDA:
    _ssm_prefix = _require_env("SSM_PREFIX")
    _ssm_params = _get_ssm_parameters(_ssm_prefix, _SSM_KEYS)
    LINE_CHANNEL_SECRET: str = _ssm_params["LINE_CHANNEL_SECRET"]
    LINE_CHANNEL_ACCESS_TOKEN: str = _ssm_params["LINE_CHANNEL_ACCESS_TOKEN"]
    ANTHROPIC_API_KEY: str = _ssm_params["ANTHROPIC_API_KEY"]
    GAS_WEBAPP_URL: str = _ssm_params["GAS_WEBAPP_URL"]
    GAS_MAIL_WEBAPP_URL: str = _ssm_params["GAS_MAIL_WEBAPP_URL"]
else:
    LINE_CHANNEL_SECRET = _require_env("LINE_CHANNEL_SECRET")
    LINE_CHANNEL_ACCESS_TOKEN = _require_env("LINE_CHANNEL_ACCESS_TOKEN")
    ANTHROPIC_API_KEY = _require_env("ANTHROPIC_API_KEY")
    GAS_WEBAPP_URL = _require_env("GAS_WEBAPP_URL")
    GAS_MAIL_WEBAPP_URL = _require_env("GAS_MAIL_WEBAPP_URL")
