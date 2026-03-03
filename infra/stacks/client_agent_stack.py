from aws_cdk import (
    BundlingOptions,
    CfnOutput,
    Duration,
    Stack,
    Tags,
    aws_lambda as lambda_,
)
from constructs import Construct

BACKEND_SRC_PATH = "../backend/src"

LAMBDA_TIMEOUT_SECONDS = 90
LAMBDA_MEMORY_MB = 256
LAMBDA_RUNTIME = lambda_.Runtime.PYTHON_3_11


class ClientAgentStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        app_name: str,
        app_env: str,
        line_channel_secret: str,
        line_channel_access_token: str,
        anthropic_api_key: str,
        gas_webapp_url: str,
        gas_mail_webapp_url: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        webhook_function, function_url = self._create_webhook_function(
            app_env=app_env,
            line_channel_secret=line_channel_secret,
            line_channel_access_token=line_channel_access_token,
            anthropic_api_key=anthropic_api_key,
            gas_webapp_url=gas_webapp_url,
            gas_mail_webapp_url=gas_mail_webapp_url,
        )

        self._add_outputs(function_url)

        Tags.of(self).add("App", app_name)
        Tags.of(self).add("Env", app_env)

    def _create_webhook_function(
        self,
        app_env: str,
        line_channel_secret: str,
        line_channel_access_token: str,
        anthropic_api_key: str,
        gas_webapp_url: str,
        gas_mail_webapp_url: str,
    ) -> tuple[lambda_.Function, lambda_.FunctionUrl]:
        fn = lambda_.Function(
            self,
            "WebhookFunction",
            runtime=LAMBDA_RUNTIME,
            handler="lambda_handler.handler",
            code=lambda_.Code.from_asset(
                BACKEND_SRC_PATH,
                bundling=BundlingOptions(
                    image=LAMBDA_RUNTIME.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output"
                        " --platform manylinux2014_x86_64"
                        " --implementation cp"
                        " --python-version 3.11"
                        " --only-binary=:all:"
                        " && cp -r . /asset-output",
                    ],
                ),
            ),
            timeout=Duration.seconds(LAMBDA_TIMEOUT_SECONDS),
            memory_size=LAMBDA_MEMORY_MB,
            environment={
                "APP_ENV": app_env,
                "LINE_CHANNEL_SECRET": line_channel_secret,
                "LINE_CHANNEL_ACCESS_TOKEN": line_channel_access_token,
                "ANTHROPIC_API_KEY": anthropic_api_key,
                "GAS_WEBAPP_URL": gas_webapp_url,
                "GAS_MAIL_WEBAPP_URL": gas_mail_webapp_url,
            },
        )

        function_url = fn.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE,
        )

        return fn, function_url

    def _add_outputs(
        self,
        function_url: lambda_.FunctionUrl,
    ) -> None:
        CfnOutput(
            self,
            "WebhookUrl",
            description="Lambda Function URL (set this as LINE Webhook URL)",
            value=function_url.url,
        )
