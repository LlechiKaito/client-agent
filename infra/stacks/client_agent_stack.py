from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    Tags,
    aws_lambda as lambda_,
    aws_s3 as s3,
)
from constructs import Construct

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

        webhook_function = self._create_webhook_function(app_env)
        frontend_bucket = self._create_frontend_bucket()

        self._add_outputs(webhook_function, frontend_bucket)

        Tags.of(self).add("App", app_name)
        Tags.of(self).add("Env", app_env)

    def _create_webhook_function(self, app_env: str) -> lambda_.Function:
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
            },
        )

        fn.add_function_url(auth_type=lambda_.FunctionUrlAuthType.NONE)

        return fn

    def _create_frontend_bucket(self) -> s3.Bucket:
        bucket = s3.Bucket(
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

        return bucket

    def _add_outputs(
        self,
        webhook_function: lambda_.Function,
        frontend_bucket: s3.Bucket,
    ) -> None:
        CfnOutput(
            self,
            "WebhookUrl",
            description="Lambda Function URL (set this as LINE Webhook URL)",
            value=webhook_function.function_url or "",
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
