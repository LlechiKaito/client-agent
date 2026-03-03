import importlib
from unittest.mock import MagicMock, patch

import pytest

SSM_PREFIX = "/client-agent/"

MOCK_SSM_RESPONSE = {
    "Parameters": [
        {"Name": f"{SSM_PREFIX}LINE_CHANNEL_SECRET", "Value": "test-secret"},
        {"Name": f"{SSM_PREFIX}LINE_CHANNEL_ACCESS_TOKEN", "Value": "test-token"},
        {"Name": f"{SSM_PREFIX}ANTHROPIC_API_KEY", "Value": "test-key"},
        {"Name": f"{SSM_PREFIX}GAS_WEBAPP_URL", "Value": "https://example.com/gas"},
        {"Name": f"{SSM_PREFIX}GAS_MAIL_WEBAPP_URL", "Value": "https://example.com/mail"},
    ],
}


@pytest.fixture
def lambda_env():
    mock_ssm = MagicMock()
    mock_ssm.get_parameters.return_value = MOCK_SSM_RESPONSE
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
        ),
        patch.dict("sys.modules", {"boto3": mock_boto3}),
    ):
        import config.settings as settings_module

        importlib.reload(settings_module)
        yield


def test_lambda_handler_is_callable(lambda_env) -> None:
    import lambda_handler

    importlib.reload(lambda_handler)
    assert callable(lambda_handler.handler)


def test_settings_does_not_require_host_port_on_lambda(lambda_env) -> None:
    import config.settings as settings_module

    importlib.reload(settings_module)
    assert settings_module.IS_LAMBDA is True
