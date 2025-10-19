"""
DynamoDB service for storing parsed transactions and PDF metadata.

This module handles all DynamoDB operations including storing PDFs,
transactions, and querying historical data.
"""

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

import boto3
from botocore.exceptions import ClientError

from ..models.transaction import Transaction

logger = logging.getLogger(__name__)


class DynamoDBService:
    """Service for interacting with DynamoDB to store transaction data"""

    def __init__(
        self,
        table_name: str = "transaction-parser-transactions",
        region_name: str = "eu-west-1",
    ):
        """
        Initialize DynamoDB service.

        Args:
            table_name: Name of the DynamoDB table
            region_name: AWS region
        """
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.table = self.dynamodb.Table(table_name)
        self.table_name = table_name
        logger.info(f"Initialized DynamoDB service for table {table_name}")

    def store_pdf_with_transactions(
        self,
        pdf_sha256: str,
        pdf_filename: str,
        pdf_size: int,
        transactions: List[Transaction],
        parsed_at: str,
    ) -> str:
        """
        Store PDF metadata and all associated transactions in DynamoDB.

        Uses a batch write operation to store the PDF record and all transactions.

        Args:
            pdf_sha256: SHA256 hash of the PDF (used as partition key)
            pdf_filename: Original filename
            pdf_size: Size of PDF in bytes
            transactions: List of parsed transactions
            parsed_at: ISO timestamp of when parsing occurred

        Returns:
            The PDF ID (same as SHA256)

        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            pdf_id = pdf_sha256

            # Prepare PDF metadata record
            pdf_record = {
                "pk": f"PDF#{pdf_id}",
                "sk": "METADATA",
                "entityType": "PDF",
                "pdfId": pdf_id,
                "filename": pdf_filename,
                "sha256": pdf_sha256,
                "fileSize": pdf_size,
                "parsedAt": parsed_at,
                "transactionCount": len(transactions),
                "createdAt": datetime.now().isoformat(),
            }

            # Prepare transaction records
            transaction_records = []
            for idx, txn in enumerate(transactions):
                record = {
                    "pk": f"PDF#{pdf_id}",
                    "sk": f"TXN#{idx:04d}",
                    "entityType": "TRANSACTION",
                    "pdfId": pdf_id,
                    "transactionIndex": idx,
                    "date": txn.date,
                    "isin": txn.isin,
                    "productName": txn.product_name,
                    "quantity": str(txn.quantity),  # Store as string to preserve precision
                    "amountEuros": str(txn.amount_euros),
                    "transactionType": txn.transaction_type,
                    "parsedAt": parsed_at,
                }
                transaction_records.append(record)

            # Use batch write to store all items
            with self.table.batch_writer() as batch:
                # Write PDF metadata
                batch.put_item(Item=pdf_record)

                # Write all transactions
                for record in transaction_records:
                    batch.put_item(Item=record)

            logger.info(
                f"Stored PDF {pdf_id} with {len(transactions)} transactions in DynamoDB"
            )
            return pdf_id

        except ClientError as e:
            logger.error(f"Error storing data in DynamoDB: {e}")
            raise

    def get_pdf_metadata(self, pdf_id: str) -> Optional[dict]:
        """
        Retrieve PDF metadata by ID.

        Args:
            pdf_id: The PDF ID (SHA256 hash)

        Returns:
            PDF metadata dict or None if not found
        """
        try:
            response = self.table.get_item(
                Key={"pk": f"PDF#{pdf_id}", "sk": "METADATA"}
            )
            return response.get("Item")

        except ClientError as e:
            logger.error(f"Error retrieving PDF metadata: {e}")
            return None

    def get_transactions_for_pdf(self, pdf_id: str) -> List[Transaction]:
        """
        Retrieve all transactions for a specific PDF.

        Args:
            pdf_id: The PDF ID (SHA256 hash)

        Returns:
            List of Transaction objects
        """
        try:
            response = self.table.query(
                KeyConditionExpression="pk = :pk AND begins_with(sk, :sk_prefix)",
                ExpressionAttributeValues={
                    ":pk": f"PDF#{pdf_id}",
                    ":sk_prefix": "TXN#",
                },
            )

            records = response.get("Items", [])

            # Convert DynamoDB records to Transaction objects
            transactions = []
            for record in records:
                transactions.append(Transaction(
                    date=record["date"],
                    isin=record["isin"],
                    product_name=record["productName"],
                    quantity=Decimal(record["quantity"]),
                    amount_euros=Decimal(record["amountEuros"]),
                    transaction_type=record["transactionType"]
                ))

            return transactions

        except ClientError as e:
            logger.error(f"Error retrieving transactions: {e}")
            return []
        except Exception as e:
            logger.error(f"Error converting DynamoDB records to Transactions: {e}")
            return []

    def check_pdf_exists(self, pdf_sha256: str) -> bool:
        """
        Check if a PDF with the given hash has already been processed.

        Args:
            pdf_sha256: SHA256 hash of the PDF

        Returns:
            True if PDF exists, False otherwise
        """
        try:
            response = self.table.get_item(
                Key={"pk": f"PDF#{pdf_sha256}", "sk": "METADATA"}
            )
            return "Item" in response

        except ClientError as e:
            logger.error(f"Error checking PDF existence: {e}")
            return False

    def query_transactions_by_isin(
        self, isin: str, limit: int = 100
    ) -> List[dict]:
        """
        Query transactions by ISIN using the GSI.

        Args:
            isin: The ISIN code to search for
            limit: Maximum number of results

        Returns:
            List of transaction records
        """
        try:
            response = self.table.query(
                IndexName="isin-index",
                KeyConditionExpression="isin = :isin",
                ExpressionAttributeValues={":isin": isin},
                Limit=limit,
            )
            return response.get("Items", [])

        except ClientError as e:
            logger.error(f"Error querying transactions by ISIN: {e}")
            return []
