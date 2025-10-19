"""
Script to create the DynamoDB table for the transaction parser.

Run this script to set up the DynamoDB table in your AWS account.
"""

import boto3
from botocore.exceptions import ClientError


def create_table(region_name="eu-west-1"):
    """Create the DynamoDB table for storing transactions"""

    dynamodb = boto3.client("dynamodb", region_name=region_name)

    table_name = "transaction-parser-transactions"

    try:
        # Check if table already exists
        existing_tables = dynamodb.list_tables()["TableNames"]
        if table_name in existing_tables:
            print(f"✓ Table '{table_name}' already exists")
            return

        print(f"Creating DynamoDB table '{table_name}'...")

        # Create table
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},  # Partition key
                {"AttributeName": "sk", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
                {"AttributeName": "isin", "AttributeType": "S"},
                {"AttributeName": "date", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "isin-index",
                    "KeySchema": [
                        {"AttributeName": "isin", "KeyType": "HASH"},
                        {"AttributeName": "date", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5,
                    },
                }
            ],
            BillingMode="PAY_PER_REQUEST",
            StreamSpecification={
                "StreamEnabled": False,
            },
            Tags=[
                {"Key": "Application", "Value": "TransactionParser"},
                {"Key": "Environment", "Value": "Development"},
            ],
        )

        print(f"✓ Table '{table_name}' created successfully!")
        print(f"  ARN: {response['TableDescription']['TableArn']}")
        print(f"  Status: {response['TableDescription']['TableStatus']}")
        print(
            "\nWait for the table to become ACTIVE before using it (usually takes 10-30 seconds)"
        )

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f"✓ Table '{table_name}' already exists")
        else:
            print(f"✗ Error creating table: {e}")
            raise


if __name__ == "__main__":
    import sys

    region = sys.argv[1] if len(sys.argv) > 1 else "eu-west-1"

    print(f"Setting up DynamoDB in region: {region}")
    print("=" * 60)

    create_table(region_name=region)

    print("\n" + "=" * 60)
    print("Setup complete!")
    print("\nTable schema:")
    print("  Primary Key: pk (partition) + sk (sort)")
    print("  GSI: isin-index (isin + date)")
    print("\nAccess patterns:")
    print("  1. Get PDF metadata: pk=PDF#{pdf_id}, sk=METADATA")
    print("  2. Get all transactions for PDF: pk=PDF#{pdf_id}, sk starts with TXN#")
    print("  3. Query by ISIN: Use isin-index GSI")
