from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_apigateway as apigw,
    Duration,
    CfnOutput,
    RemovalPolicy,
)
from aws_cdk.aws_lambda import Runtime
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct

class MockDataLambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for storing generated data
        data_bucket = s3.Bucket(
            self, "MockDataBucket",
            bucket_name=f"mock-data-{self.account}-{self.region}",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Lambda function
        mock_data_lambda = PythonFunction(
            self, "MockDataLambda",
            entry="../lambda_function",       # folder containing lambda_function.py + requirements.txt
            index="lambda_function.py",       # your Lambda file
            handler="lambda_handler",         # function name in that file
            runtime=Runtime.PYTHON_3_11,      # recommended newer runtime
            timeout=Duration.minutes(15),
            memory_size=256,
            environment={
                "BUCKET_NAME": data_bucket.bucket_name
            }
        )

        # Grant Lambda write permissions to the S3 bucket
        data_bucket.grant_write(mock_data_lambda)

        # API Gateway
        api = apigw.LambdaRestApi(
            self, "MockDataApi",
            handler=mock_data_lambda,
            proxy=False
        )

        # /single endpoint
        single = api.root.add_resource("single")
        single.add_method("GET")
        single.add_method("POST")

        # /bulk endpoint
        bulk = api.root.add_resource("bulk")
        bulk.add_method("GET")

        # Output the API URL
        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="Mock Data API URL"
        )
