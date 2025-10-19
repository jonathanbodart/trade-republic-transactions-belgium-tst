"""
LLM-based transaction parser using AWS Bedrock.

This module provides the main interface for parsing financial transactions
from PDF text using Large Language Models (LLMs) via AWS Bedrock.
"""

import logging
from typing import List

from ..models.transaction import Transaction
from .bedrock_client import BedrockClient
from .prompts import build_parsing_prompt
from .response_parser import ResponseParser

logger = logging.getLogger(__name__)


class LLMParser:
    """
    Uses AWS Bedrock (Claude) to parse transaction data from PDF text.

    This class provides a high-level interface for extracting structured
    transaction data from unstructured PDF text using LLMs.
    """

    def __init__(
        self,
        region_name: str = "eu-west-1",
        model_id: str = "eu.anthropic.claude-haiku-4-5-20251001-v1:0",
    ):
        """
        Initialize the LLM parser with AWS Bedrock.

        Args:
            region_name: AWS region for Bedrock service
            model_id: Claude model ID or inference profile to use
        """
        self.bedrock_client = BedrockClient(
            region_name=region_name, model_id=model_id
        )
        logger.info(
            f"Initialized LLM parser with model {model_id} in region {region_name}"
        )

    def parse_transactions(self, pdf_text: str) -> List[Transaction]:
        """
        Parse transactions from PDF text using Claude.

        Args:
            pdf_text: Extracted text from PDF document

        Returns:
            List of Transaction objects parsed from the text

        Raises:
            ValueError: If the response cannot be parsed
            Exception: For other errors during parsing
        """
        try:
            # Build the prompt with the PDF text
            prompt = build_parsing_prompt(pdf_text)

            # Call the LLM
            response = self.bedrock_client.invoke(prompt)

            # Parse the response into Transaction objects
            transactions = ResponseParser.parse_transactions(response)

            logger.info(f"Successfully parsed {len(transactions)} transactions")
            return transactions

        except Exception as e:
            logger.error(f"Error parsing transactions with LLM: {e}")
            raise
