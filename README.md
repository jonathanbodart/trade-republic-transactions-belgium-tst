# Trade Republic Transaction Parser

An AI-powered tool to parse PDF bank statements from Trade Republic and extract structured transaction data.

## Features

- **Smart PDF Processing**: Efficient text extraction + Claude analysis
- **AI-Powered Extraction**: Uses AWS Bedrock (Claude Haiku 4.5) for intelligent parsing
- **Prompt Caching**: 90% cost savings on repeated calls via cached system prompts
- **System Prompt Architecture**: Clean separation of instructions and data
- **Structured Output**: ISIN, product names, quantities, amounts, and transaction types
- **Web Interface**: Modern React UI for upload and viewing
- **Data Aggregation**: Optional grouping by ISIN and transaction type
- **Export**: Download as JSON or CSV
- **Production Ready**: DynamoDB persistence, S3 storage, CDK infrastructure

## Architecture

### Backend (Python)
- **FastAPI**: REST API framework
- **AWS Bedrock**: Claude LLM for intelligent PDF parsing
- **pdfplumber**: PDF text extraction
- **boto3**: AWS SDK for S3 and DynamoDB

### Frontend (React + TypeScript)
- PDF upload interface
- Transaction data table
- Export functionality

### Infrastructure (AWS CDK)
- Lambda functions for API endpoints
- API Gateway
- S3 for PDF storage
- DynamoDB for transaction data
- IAM roles and policies

## Project Structure

```
registration-tst/
├── backend/           # Python backend
│   ├── src/
│   │   ├── api/      # FastAPI routes
│   │   ├── parsers/  # PDF and LLM parsing logic
│   │   ├── models/   # Data models
│   │   └── utils/    # Helper functions
│   └── requirements.txt
├── frontend/          # React + TypeScript
│   ├── src/
│   └── package.json
├── infrastructure/    # AWS CDK
│   └── app.py
└── samples/          # Sample PDFs
```

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- AWS account with Bedrock access (Claude 3.5 Sonnet enabled)
- AWS CLI configured (`aws configure`)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure AWS credentials
aws configure  # Enter your AWS credentials

# Run the backend
uvicorn src.api.main:app --reload
```

Backend will be available at `http://localhost:8000`

### 2. Frontend Setup
Open a new terminal:
```bash
cd frontend
npm install
npm start
```

Frontend will open at `http://localhost:3000`

### 3. Set Up DynamoDB (Optional but Recommended)
```bash
cd backend
python setup_dynamodb.py eu-west-1
```

This enables:
- Deduplication (same PDF won't be parsed twice)
- Historical querying by ISIN
- Fast retrieval of previously parsed PDFs

### 4. Test It!
1. Open `http://localhost:3000` in your browser
2. Upload a Trade Republic PDF statement
3. Click "Upload & Parse"
4. View structured transactions and export to JSON/CSV
5. Upload the same PDF again - it will be retrieved from cache!

## Deployment to AWS

```bash
cd infrastructure
pip install -r requirements.txt
cdk bootstrap  # First time only
cdk deploy
```

See [Infrastructure README](infrastructure/README.md) for details.

## License

MIT
