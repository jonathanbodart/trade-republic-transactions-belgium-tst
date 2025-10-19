# Development Guide

This guide will help you set up and run the Transaction Parser locally for development.

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials (for Bedrock access)
aws configure
# Enter your AWS Access Key ID, Secret Key, and set region to us-east-1

# Run the backend
uvicorn src.api.main:app --reload
```

The backend will be available at `http://localhost:8000`

### 2. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will open at `http://localhost:3000`

### 3. Test the Application

1. Open your browser to `http://localhost:3000`
2. Upload the sample PDF from `/Users/jonathanbodart/Desktop/Account statement.pdf`
3. Click "Upload & Parse"
4. View the parsed transactions

## Backend API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Parse PDF
```bash
curl -X POST \
  http://localhost:8000/parse \
  -F "file=@/path/to/statement.pdf" \
  -F "aggregate=true"
```

### Parse Text (for testing)
```bash
curl -X POST \
  http://localhost:8000/parse-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "02 Sep 2025 Trade Savings plan execution IE00B5BMR087 iShares Core S&P 500, quantity: 0.085178 €50.00",
    "aggregate": false
  }'
```

## Project Structure

```
registration-tst/
├── backend/
│   ├── src/
│   │   ├── api/          # FastAPI application
│   │   │   └── main.py   # Main API file
│   │   ├── models/       # Pydantic models
│   │   │   └── transaction.py
│   │   ├── parsers/      # PDF and LLM parsing
│   │   │   ├── pdf_parser.py
│   │   │   └── llm_parser.py
│   │   └── utils/        # Helper functions
│   │       └── aggregator.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   │   ├── FileUpload.tsx
│   │   │   └── TransactionTable.tsx
│   │   ├── types/        # TypeScript types
│   │   │   └── transaction.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   └── package.json
└── infrastructure/
    ├── stacks/
    │   └── transaction_parser_stack.py
    ├── app.py
    └── cdk.json
```

## How It Works

### 1. PDF Upload
- User uploads a Trade Republic PDF statement via the React frontend
- Frontend sends the PDF to the backend via multipart/form-data

### 2. Text Extraction
- `PDFParser` uses `pdfplumber` to extract text from all PDF pages
- Text is concatenated with page markers

### 3. LLM Parsing
- `LLMParser` sends the extracted text to AWS Bedrock (Claude)
- Claude parses the unstructured text and returns structured JSON
- Prompt includes specific instructions for:
  - Identifying ISINs (including Bitcoin's XF000BTC0017)
  - Extracting quantities and amounts
  - Determining transaction types (BUY/SELL/DIVIDEND)

### 4. Aggregation (Optional)
- If requested, transactions are aggregated by ISIN and type
- Sums quantities and amounts for each group

### 5. Display
- Frontend displays transactions in a table
- Color-coded badges for transaction types
- Export to JSON/CSV functionality

## AWS Bedrock Configuration

The application uses Claude 3.5 Sonnet via AWS Bedrock. Required setup:

1. **Enable Bedrock Access**:
   - Go to AWS Console → Bedrock
   - Navigate to "Model access"
   - Request access to "Claude 3.5 Sonnet v2"

2. **AWS Credentials**:
   - Ensure your AWS credentials have `bedrock:InvokeModel` permission
   - Set up credentials via `aws configure` or environment variables

3. **Region**:
   - The default region is `us-east-1`
   - You can change this in `backend/src/parsers/llm_parser.py`

## Environment Variables

### Backend
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `AWS_DEFAULT_REGION` - AWS region (default: us-east-1)

### Frontend
- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000)

## Testing

### Test Backend Directly

```python
# test_parser.py
from backend.src.parsers import PDFParser, LLMParser

# Extract text from PDF
with open('/Users/jonathanbodart/Desktop/Account statement.pdf', 'rb') as f:
    text = PDFParser.extract_text(f)
    print(f"Extracted {len(text)} characters")

# Parse with LLM
llm = LLMParser()
transactions = llm.parse_transactions(text)
print(f"Found {len(transactions)} transactions")

for txn in transactions[:3]:
    print(f"{txn.date} | {txn.isin} | {txn.transaction_type} | €{txn.amount_euros}")
```

### Run Tests (if implemented)

```bash
cd backend
pytest
```

## Deployment

See the [Infrastructure README](infrastructure/README.md) for deployment instructions.

## Troubleshooting

### Backend Issues

**Error: "Import pydantic could not be resolved"**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Error: "Unable to locate credentials"**
- Run `aws configure` and enter your credentials
- Or set environment variables

**Error: "Access denied to Bedrock model"**
- Request model access in AWS Console → Bedrock → Model access
- Ensure IAM user/role has `bedrock:InvokeModel` permission

### Frontend Issues

**Error: "Network Error" when uploading PDF**
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify API URL in frontend

**Large PDFs timeout**
- Increase timeout in `frontend/src/components/FileUpload.tsx`
- Adjust Lambda timeout in infrastructure if deployed

## Next Steps

1. Add database persistence (DynamoDB integration)
2. Implement authentication
3. Add unit tests
4. Deploy to AWS
5. Add support for other bank formats
6. Implement transaction analytics
