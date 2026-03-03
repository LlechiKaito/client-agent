from aws_cdk import (
    BundlingOptions,
    CfnOutput,
    Duration,
    Stack,
    Tags,
    aws_iam as iam,
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
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ssm_prefix = f"/{app_name}/"

        webhook_function, function_url = self._create_webhook_function(
            app_env=app_env,
            ssm_prefix=ssm_prefix,
        )

        self._grant_ssm_read(webhook_function, ssm_prefix)
        self._add_outputs(function_url)

        Tags.of(self).add("App", app_name)
        Tags.of(self).add("Env", app_env)

    def _create_webhook_function(
        self,
        app_env: str,
        ssm_prefix: str,
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
                "SSM_PREFIX": ssm_prefix,
            },
        )

        function_url = fn.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE,
        )

        return fn, function_url

    def _grant_ssm_read(
        self,
        function: lambda_.Function,
        ssm_prefix: str,
    ) -> None:
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameters"],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter{ssm_prefix}*",
                ],
            ),
        )

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
