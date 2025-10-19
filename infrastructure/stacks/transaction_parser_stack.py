from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
from constructs import Construct


class TransactionParserStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 Bucket for PDF storage
        pdf_bucket = s3.Bucket(
            self, "PDFBucket",
            bucket_name=f"transaction-parser-pdfs-{self.account}",
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    enabled=True,
                    expiration=Duration.days(90)  # Auto-delete PDFs after 90 days
                )
            ]
        )

        # DynamoDB Table for transactions
        transactions_table = dynamodb.Table(
            self, "TransactionsTable",
            table_name="transaction-parser-transactions",
            partition_key=dynamodb.Attribute(
                name="pk",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="sk",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True
        )

        # Add GSI for querying by ISIN
        transactions_table.add_global_secondary_index(
            index_name="isin-index",
            partition_key=dynamodb.Attribute(
                name="isin",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="date",
                type=dynamodb.AttributeType.STRING
            )
        )

        # IAM Role for Lambda
        lambda_role = iam.Role(
            self, "ParserLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ]
        )

        # Grant Lambda access to S3 bucket
        pdf_bucket.grant_read_write(lambda_role)

        # Grant Lambda access to DynamoDB table
        transactions_table.grant_read_write_data(lambda_role)

        # Grant Lambda access to Bedrock
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                resources=[
                    f"arn:aws:bedrock:{self.region}::foundation-model/eu.anthropic.claude-haiku-4-5-20251001-v1:0"
                ]
            )
        )

        # Lambda Layer for dependencies

        # Lambda Function for PDF parsing
        # parser_lambda = _lambda.Function(
            #     self, "ParserFunction",
            #     function_name="transaction-parser",
            #     runtime=_lambda.Runtime.PYTHON_3_12,
            #     handler="src.api.main.handler",
            #     code=_lambda.Code.from_asset("../backend"),
            #     role=lambda_role,
            #     timeout=Duration.seconds(300),  # 5 minutes for LLM processing
            #     memory_size=1024,
            #     environment={
            #         "PDF_BUCKET": pdf_bucket.bucket_name,
            #         "TRANSACTIONS_TABLE": transactions_table.table_name,
            #         "AWS_REGION_NAME": self.region
            #     },
            #     layers=[dependencies_layer]
            # )

            # 

        # API Gateway
        api = apigw.RestApi(
            self, "TransactionParserAPI",
            rest_api_name="Transaction Parser API",
            description="API for parsing Trade Republic transaction PDFs",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["*"]
            )
        )

        # Lambda integration
        # parser_integration = apigw.LambdaIntegration(parser_lambda)

        # API Resources
        # parse_resource = api.root.add_resource("parse")
        # parse_resource.add_method("POST", parser_integration)

        # health_resource = api.root.add_resource("health")
        # health_resource.add_method("GET", parser_integration)

        # CloudFront distribution for frontend (optional - can be added later)
        # For now, frontend can be hosted on S3 or served locally

        # Outputs
        CfnOutput(
            self, "APIEndpoint",
            value=api.url,
            description="API Gateway endpoint URL"
        )

        CfnOutput(
            self, "PDFBucketName",
            value=pdf_bucket.bucket_name,
            description="S3 bucket for PDF storage"
        )

        CfnOutput(
            self, "TransactionsTableName",
            value=transactions_table.table_name,
            description="DynamoDB table for transactions"
        )
