#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.client_agent_stack import ClientAgentStack

app = cdk.App()

app_name = app.node.try_get_context("app_name") or "client-agent"
app_env = app.node.try_get_context("app_env") or "production"

ClientAgentStack(
    app,
    f"{app_name}-stack",
    app_name=app_name,
    app_env=app_env,
    frontend_url=app.node.try_get_context("frontend_url") or "",
    line_channel_secret=app.node.try_get_context("line_channel_secret") or "",
    line_channel_access_token=app.node.try_get_context("line_channel_access_token") or "",
    anthropic_api_key=app.node.try_get_context("anthropic_api_key") or "",
    gas_webapp_url=app.node.try_get_context("gas_webapp_url") or "",
    gas_mail_webapp_url=app.node.try_get_context("gas_mail_webapp_url") or "",
)

app.synth()
