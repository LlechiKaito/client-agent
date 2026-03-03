import importlib
from unittest.mock import MagicMock, patch

import pytest

SSM_PREFIX = "/client-agent/"

MOCK_SSM_RESPONSE = {
    "Parameters": [
        {"Name": f"{SSM_PREFIX}LINE_CHANNEL_SECRET", "Value": "ssm-secret"},
        {"Name": f"{SSM_PREFIX}LINE_CHANNEL_ACCESS_TOKEN", "Value": "ssm-token"},
        {"Name": f"{SSM_PREFIX}ANTHROPIC_API_KEY", "Value": "ssm-api-key"},
        {"Name": f"{SSM_PREFIX}GAS_WEBAPP_URL", "Value": "https://ssm.example.com/gas"},
        {"Name": f"{SSM_PREFIX}GAS_MAIL_WEBAPP_URL", "Value": "https://ssm.example.com/mail"},
    ],
}


def _reload_settings_with_ssm(mock_ssm_response: dict) -> "module":
    mock_ssm = MagicMock()
    mock_ssm.get_parameters.return_value = mock_ssm_response
    mock_boto3 = MagicMock()
    mock_boto3.client.return_value = mock_ssm

    with (
        patch.dict(
            "os.environ",
            {
                "AWS_LAMBDA_FUNCTION_NAME": "test-function",
                "APP_ENV": "test",
                "SSM_PREFIX": SSM_PREFIX,
            },
            clear=True,
        ),
        patch.dict("sys.modules", {"boto3": mock_boto3}),
    ):
        import config.settings as settings_module

        importlib.reload(settings_module)
        return settings_module


def test_should_read_secrets_from_ssm_on_lambda() -> None:
    settings = _reload_settings_with_ssm(MOCK_SSM_RESPONSE)

    assert settings.LINE_CHANNEL_SECRET == "ssm-secret"
    assert settings.LINE_CHANNEL_ACCESS_TOKEN == "ssm-token"
    assert settings.ANTHROPIC_API_KEY == "ssm-api-key"
    assert settings.GAS_WEBAPP_URL == "https://ssm.example.com/gas"
    assert settings.GAS_MAIL_WEBAPP_URL == "https://ssm.example.com/mail"


def test_should_raise_when_ssm_parameter_missing() -> None:
    incomplete_response = {
        "Parameters": [
            {"Name": f"{SSM_PREFIX}LINE_CHANNEL_SECRET", "Value": "secret"},
        ],
    }

    with pytest.raises(RuntimeError, match="SSM parameters not found"):
        _reload_settings_with_ssm(incomplete_response)


def test_should_read_from_env_when_not_lambda() -> None:
    with patch.dict(
        "os.environ",
        {
            "APP_HOST": "0.0.0.0",
            "APP_PORT": "8000",
            "APP_ENV": "test",
            "LINE_CHANNEL_SECRET": "env-secret",
            "LINE_CHANNEL_ACCESS_TOKEN": "env-token",
            "ANTHROPIC_API_KEY": "env-key",
            "GAS_WEBAPP_URL": "https://env.example.com/gas",
            "GAS_MAIL_WEBAPP_URL": "https://env.example.com/mail",
        },
        clear=True,
    ):
        import config.settings as settings_module

        importlib.reload(settings_module)

        assert settings_module.IS_LAMBDA is False
        assert settings_module.LINE_CHANNEL_SECRET == "env-secret"
        assert settings_module.ANTHROPIC_API_KEY == "env-key"
