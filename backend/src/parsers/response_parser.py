"""
Response parser for LLM-generated transaction data.

This module handles parsing and validation of JSON responses
from the LLM, converting them into Transaction objects.
"""

import json
import logging
from decimal import Decimal
from typing import Any, Dict, List

from ..models.transaction import Transaction

logger = logging.getLogger(__name__)


class ResponseParser:
    """Parser for LLM responses containing transaction data"""

    @staticmethod
    def parse_transactions(response_text: str) -> List[Transaction]:
        """
        Parse LLM response into Transaction objects.

        Args:
            response_text: Raw text response from LLM

        Returns:
            List of Transaction objects

        Raises:
            ValueError: If the response cannot be parsed or is invalid
        """
        try:
            json_text = ResponseParser._extract_json(response_text)
            transactions_data = json.loads(json_text)

            if not isinstance(transactions_data, list):
                raise ValueError("Response must be a JSON array")

            return ResponseParser._convert_to_transactions(transactions_data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            raise

    @staticmethod
    def _extract_json(response_text: str) -> str:
        """
        Extract JSON array from response text.

        Handles cases where the LLM may include additional text
        before or after the JSON array.

        Args:
            response_text: Raw response text

        Returns:
            Extracted JSON string

        Raises:
            ValueError: If no JSON array is found
        """
        response_text = response_text.strip()

        # Find JSON array boundaries
        start_idx = response_text.find("[")
        end_idx = response_text.rfind("]") + 1

        if start_idx == -1 or end_idx == 0:
            logger.error(f"No JSON array found in response: {response_text}")
            raise ValueError("No JSON array found in response")

        return response_text[start_idx:end_idx]

    @staticmethod
    def _convert_to_transactions(
        transactions_data: List[Dict[str, Any]]
    ) -> List[Transaction]:
        """
        Convert parsed JSON data to Transaction objects.

        Args:
            transactions_data: List of transaction dictionaries

        Returns:
            List of Transaction objects

        Raises:
            ValueError: If data cannot be converted to transactions
        """
        transactions = []

        for idx, item in enumerate(transactions_data):
            try:
                # Convert string decimals to Decimal type
                item["quantity"] = Decimal(str(item["quantity"]))
                item["amount_euros"] = Decimal(str(item["amount_euros"]))

                transaction = Transaction(**item)
                transactions.append(transaction)

            except (KeyError, TypeError, ValueError) as e:
                logger.error(
                    f"Error converting transaction {idx + 1}: {e}. Data: {item}"
                )
                raise ValueError(
                    f"Invalid transaction data at index {idx + 1}: {e}"
                )

        return transactions
