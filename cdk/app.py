#!/usr/bin/env python3
import aws_cdk as cdk
from mock_data_lambda_stack import MockDataLambdaStack

app = cdk.App()
MockDataLambdaStack(app, "MockDataLambdaStack")
app.synth()