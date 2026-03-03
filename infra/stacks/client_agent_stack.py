from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    Tags,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
)
from constructs import Construct

FRONTEND_DIST_PATH = "../frontend/dist"

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

        frontend_bucket = self._create_frontend_bucket()
        self._deploy_frontend(frontend_bucket)

        webhook_function, function_url = self._create_webhook_function(
            app_env=app_env,
            frontend_url=frontend_bucket.bucket_website_url,
            line_channel_secret=line_channel_secret,
            line_channel_access_token=line_channel_access_token,
            anthropic_api_key=anthropic_api_key,
            gas_webapp_url=gas_webapp_url,
            gas_mail_webapp_url=gas_mail_webapp_url,
        )

        self._add_outputs(function_url, frontend_bucket)

        Tags.of(self).add("App", app_name)
        Tags.of(self).add("Env", app_env)

    def _create_webhook_function(
        self,
        app_env: str,
        frontend_url: str,
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
            code=lambda_.Code.from_asset("../backend/src"),
            timeout=Duration.seconds(LAMBDA_TIMEOUT_SECONDS),
            memory_size=LAMBDA_MEMORY_MB,
            environment={
                "APP_ENV": app_env,
                "FRONTEND_URL": frontend_url,
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

    def _create_frontend_bucket(self) -> s3.Bucket:
        return s3.Bucket(
            self,
            "FrontendBucket",
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
        )

    def _deploy_frontend(self, bucket: s3.Bucket) -> None:
        s3deploy.BucketDeployment(
            self,
            "FrontendDeployment",
            sources=[s3deploy.Source.asset(FRONTEND_DIST_PATH)],
            destination_bucket=bucket,
        )

    def _add_outputs(
        self,
        function_url: lambda_.FunctionUrl,
        frontend_bucket: s3.Bucket,
    ) -> None:
        CfnOutput(
            self,
            "WebhookUrl",
            description="Lambda Function URL (set this as LINE Webhook URL)",
            value=function_url.url,
        )
        CfnOutput(
            self,
            "FrontendUrl",
            description="S3 Website URL for frontend",
            value=frontend_bucket.bucket_website_url,
        )
        CfnOutput(
            self,
            "FrontendBucketName",
            description="S3 bucket name for frontend deployment",
            value=frontend_bucket.bucket_name,
        )
