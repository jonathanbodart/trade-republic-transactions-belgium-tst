# Infrastructure

AWS CDK infrastructure for the Transaction Parser application.

## Prerequisites

- Python 3.12+
- AWS CLI configured with appropriate credentials
- AWS CDK CLI installed (`npm install -g aws-cdk`)

## Setup

```bash
cd infrastructure
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Deploy

```bash
# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the stack
cdk deploy
```

## Resources Created

- **Lambda Function**: Handles PDF parsing with AWS Bedrock
- **API Gateway**: REST API for the application
- **S3 Bucket**: Stores uploaded PDFs
- **DynamoDB Table**: Stores parsed transaction data
- **IAM Roles**: Permissions for Lambda execution

## Useful Commands

- `cdk ls` - List all stacks
- `cdk synth` - Synthesize CloudFormation template
- `cdk deploy` - Deploy the stack
- `cdk diff` - Show differences with deployed stack
- `cdk destroy` - Remove all resources

## Environment Variables

The Lambda function uses these environment variables:

- `PDF_BUCKET` - S3 bucket for PDFs
- `TRANSACTIONS_TABLE` - DynamoDB table name
- `AWS_REGION_NAME` - AWS region

## Cost Considerations

- Lambda: Pay per invocation and compute time
- S3: Storage costs (PDFs auto-delete after 90 days)
- DynamoDB: On-demand billing
- API Gateway: Pay per API call
- Bedrock: Pay per token usage

Estimated cost for light usage: ~$5-10/month
