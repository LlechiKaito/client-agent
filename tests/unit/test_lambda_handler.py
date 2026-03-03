import importlib
from unittest.mock import patch

import pytest


@pytest.fixture
def lambda_env():
    with patch.dict(
        "os.environ",
        {
            "AWS_LAMBDA_FUNCTION_NAME": "test-function",
            "APP_ENV": "test",
        },
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
