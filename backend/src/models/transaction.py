from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """Represents a single financial transaction"""

    date: str = Field(..., description="Transaction date in format DD MMM YYYY")
    isin: str = Field(..., description="ISIN code of the financial instrument")
    product_name: str = Field(..., description="Full name of the financial product")
    quantity: Decimal = Field(..., description="Number of shares/units transacted")
    amount_euros: Decimal = Field(..., description="Total amount in euros")
    transaction_type: Literal["BUY", "SELL", "DIVIDEND"] = Field(
        ..., description="Type of transaction"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "date": "02 Sep 2025",
                "isin": "IE00B5BMR087",
                "product_name": "iShares VII plc - iShares Core S&P 500 UCITS ETF USD (Acc)",
                "quantity": "0.085178",
                "amount_euros": "50.00",
                "transaction_type": "BUY"
            }
        }


class AggregatedTransaction(BaseModel):
    """Represents aggregated transactions for a single ISIN"""

    isin: str = Field(..., description="ISIN code of the financial instrument")
    product_name: str = Field(..., description="Full name of the financial product")
    total_quantity: Decimal = Field(..., description="Total number of shares/units")
    total_amount_euros: Decimal = Field(..., description="Total amount in euros")
    transaction_type: Literal["BUY", "SELL", "DIVIDEND"] = Field(
        ..., description="Type of transaction"
    )
    transaction_count: int = Field(..., description="Number of transactions")

    class Config:
        json_schema_extra = {
            "example": {
                "isin": "IE00B5BMR087",
                "product_name": "iShares VII plc - iShares Core S&P 500 UCITS ETF USD (Acc)",
                "total_quantity": "0.335727",
                "total_amount_euros": "200.00",
                "transaction_type": "BUY",
                "transaction_count": 4
            }
        }


class ParseRequest(BaseModel):
    """Request model for PDF parsing"""

    aggregate: bool = Field(
        default=False,
        description="Whether to aggregate transactions by ISIN"
    )


class ParseResponse(BaseModel):
    """Response model for PDF parsing"""

    transactions: list[Transaction] = Field(..., description="List of parsed transactions")
    aggregated: Optional[list[AggregatedTransaction]] = Field(
        None, description="Aggregated transactions by ISIN (if requested)"
    )
    total_transactions: int = Field(..., description="Total number of transactions parsed")
    pdf_filename: str = Field(..., description="Original PDF filename")
    parsed_at: str = Field(..., description="Timestamp when parsing occurred")
