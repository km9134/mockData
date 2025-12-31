from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_apigateway as apigw,
    aws_iam as iam,
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

        # Lambda function with automatic dependency bundling
        mock_data_lambda = PythonFunction(
            self, "MockDataLambda",
            entry="../lambda_function",
            index="lambda_function.py",
            handler="lambda_handler",
            runtime=Runtime.PYTHON_3_11,
            timeout=Duration.minutes(15),
            memory_size=256,
            environment={
                "BUCKET_NAME": data_bucket.bucket_name
            }
        )

        # Grant Lambda write permissions to the S3 bucket
        data_bucket.grant_write(mock_data_lambda)
        
        # Grant Lambda permissions to create S3 buckets
        mock_data_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:CreateBucket", "s3:PutObject", "s3:PutBucketPolicy", "s3:PutBucketPublicAccessBlock"],
                resources=["arn:aws:s3:::mock-data-*", "arn:aws:s3:::mock-data-*/*"]
            )
        )

        # API Gateway
        api = apigw.LambdaRestApi(
            self, "MockDataApi",
            handler=mock_data_lambda,
            proxy=False
        )

        # /single endpoint
        single = api.root.add_resource("data")
        single.add_method("GET")

        # /bulk endpoint
        bulk = api.root.add_resource("bulk")
        bulk.add_method("GET")
        bulk.add_method("POST")

        # Output the API URL
        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="Mock Data API URL"
        )
