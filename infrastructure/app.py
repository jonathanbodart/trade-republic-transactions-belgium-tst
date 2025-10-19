#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.transaction_parser_stack import TransactionParserStack

app = cdk.App()

TransactionParserStack(
    app,
    "TransactionParserStack",
    description="Trade Republic Transaction Parser Infrastructure",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "eu-west-1"
    )
)

app.synth()
