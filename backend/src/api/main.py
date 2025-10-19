from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Optional
import io

from ..parsers import PDFParser, LLMParser
from ..models import ParseResponse, Transaction
from ..utils import aggregate_transactions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Trade Republic Transaction Parser",
    description="AI-powered PDF transaction parser using AWS Bedrock",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize parsers
pdf_parser = PDFParser()
llm_parser = LLMParser()


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
            "pdf_parser": "operational",
            "llm_parser": "operational"
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
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="File must be a PDF"
            )

        logger.info(f"Processing PDF: {file.filename}")

        # Read file content
        content = await file.read()
        pdf_file = io.BytesIO(content)

        # Extract text from PDF
        logger.info("Extracting text from PDF")
        pdf_text = pdf_parser.extract_text(pdf_file)

        if not pdf_text or len(pdf_text) < 100:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from PDF"
            )

        # Parse transactions using LLM
        logger.info("Parsing transactions with LLM")
        transactions = llm_parser.parse_transactions(pdf_text)

        if not transactions:
            raise HTTPException(
                status_code=400,
                detail="No transactions found in PDF"
            )

        # Optionally aggregate transactions
        aggregated = None
        if aggregate:
            logger.info("Aggregating transactions")
            aggregated = aggregate_transactions(transactions)

        response = ParseResponse(
            transactions=transactions,
            aggregated=aggregated,
            total_transactions=len(transactions),
            pdf_filename=file.filename,
            parsed_at=datetime.now().isoformat()
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


@app.post("/parse-text", response_model=ParseResponse)
async def parse_text(
    text: str,
    aggregate: bool = False
):
    """
    Parse transaction text directly (useful for testing)

    Args:
        text: Transaction text to parse
        aggregate: Whether to aggregate transactions

    Returns:
        ParseResponse with transactions
    """
    try:
        logger.info("Parsing transactions from text")

        transactions = llm_parser.parse_transactions(text)

        aggregated = None
        if aggregate:
            aggregated = aggregate_transactions(transactions)

        return ParseResponse(
            transactions=transactions,
            aggregated=aggregated,
            total_transactions=len(transactions),
            pdf_filename="direct_text_input",
            parsed_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error parsing text: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing text: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
