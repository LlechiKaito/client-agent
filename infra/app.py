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
)

app.synth()
