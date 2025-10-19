import hashlib
import io
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..models import ParseResponse, Transaction
from ..parsers import LLMParser
from ..parsers.pdf_parser import PDFParser
from ..storage.dynamodb_service import DynamoDBService
from ..utils import aggregate_transactions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

ddb_service = DynamoDBService()

# Initialize FastAPI app
app = FastAPI(
    title="Trade Republic Transaction Parser",
    description="AI-powered PDF transaction parser using AWS Bedrock with multimodal input and prompt caching",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM parser with prompt caching enabled
# Using Claude 3.5 Sonnet (change to Haiku 4.5 after requesting access in AWS Bedrock)
llm_parser = LLMParser(
    region_name="eu-west-1",
    model_id="eu.anthropic.claude-haiku-4-5-20251001-v1:0",
    enable_caching=True
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Trade Republic Transaction Parser",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "llm_parser": "operational",
            "multimodal_input": "enabled",
            "prompt_caching": "enabled",
            "dynamodb": "enabled"
        }
    }


@app.post("/parse", response_model=ParseResponse)
async def parse_pdf(
    file: UploadFile = File(..., description="PDF file to parse"),
    aggregate: bool = Form(False, description="Whether to aggregate transactions by ISIN")
):
    """
    Parse a Trade Republic bank statement PDF and extract transactions

    Args:
        file: PDF file upload
        aggregate: Whether to aggregate transactions by ISIN and type

    Returns:
        ParseResponse with transactions and optional aggregated data
    """
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="File must be a PDF and must have a valid filename"
            )

        logger.info(f"Processing PDF: {file.filename}")


        # Read file content
        content = await file.read()


        if len(content) < 100:
            raise HTTPException(
                status_code=400,
                detail="PDF file is too small or empty"
            )

        # Parse transactions using LLM with multimodal input (direct PDF processing)
        logger.info("Parsing transactions with LLM (multimodal PDF input with prompt caching)")

        pdf_sha256 = hashlib.sha256(content).hexdigest()
       
        if ddb_service.check_pdf_exists(pdf_sha256):
            logger.info(f"PDF already processed (SHA256: {pdf_sha256}), retrieving from database")

            transactions = ddb_service.get_transactions_for_pdf(pdf_sha256)

            pdf_metadata = ddb_service.get_pdf_metadata(pdf_sha256)
            parsed_at = pdf_metadata["parsedAt"] if pdf_metadata else datetime.now().isoformat()
        else:
            logger.info(f"Parsing new PDF with LLM")

            transactions = llm_parser.parse_transactions(content)
            parsed_at = datetime.now().isoformat()

            try:
                ddb_service.store_pdf_with_transactions(
                    pdf_sha256=pdf_sha256,
                    pdf_filename=file.filename,
                    pdf_size=len(content),
                    transactions=transactions,
                    parsed_at=parsed_at
                )
                logger.info(f"Stored PDF and transactions in DynamoDB")
            except Exception as e:
                logger.error(f"Failed to store in DynamoDB: {e}", exc_info=True)


        if not transactions:
            raise HTTPException(
                status_code=400,
                detail="No transactions found in PDF"
            )


        response = ParseResponse(
            transactions=transactions,
            total_transactions=len(transactions),
            pdfFilename=file.filename,
            parsed_at=parsed_at
        )

        logger.info(f"Successfully parsed {len(transactions)} transactions")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing PDF: {str(e)}"
        )




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
