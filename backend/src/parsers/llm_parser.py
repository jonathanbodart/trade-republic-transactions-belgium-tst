"""
LLM-based transaction parser using AWS Bedrock.

This module provides the main interface for parsing financial transactions
from PDF documents using Large Language Models (LLMs) via AWS Bedrock.

Supports multimodal input (direct PDF processing) and prompt caching for efficiency.
"""

import logging
from typing import List

from ..models.transaction import Transaction
from .bedrock_client import BedrockClient
from .prompts import get_system_prompt, get_user_prompt
from .response_parser import ResponseParser

logger = logging.getLogger(__name__)


class LLMParser:
    """
    Uses AWS Bedrock (Claude) to parse transaction data from PDF documents.

    This class provides a high-level interface for extracting structured
    transaction data from PDF files using LLMs with multimodal capabilities.

    The system prompt is cached to reduce costs and latency on repeated calls.
    """

    def __init__(
        self,
        region_name: str = "eu-west-1",
        model_id: str = "eu.anthropic.claude-haiku-4-5-20251001-v1:0",
        enable_caching: bool = True,
    ):
        """
        Initialize the LLM parser with AWS Bedrock.

        Args:
            region_name: AWS region for Bedrock service
            model_id: Claude model ID or inference profile to use
            enable_caching: Whether to enable prompt caching for system prompt
        """
        self.bedrock_client = BedrockClient(
            region_name=region_name, model_id=model_id
        )
        self.enable_caching = enable_caching
        logger.info(
            f"Initialized LLM parser with model {model_id} in region {region_name} "
            f"(caching {'enabled' if enable_caching else 'disabled'})"
        )

    def parse_transactions(self, pdf_data: bytes) -> List[Transaction]:
        """
        Parse transactions from PDF document using Claude with multimodal input.

        Args:
            pdf_data: PDF file content as bytes

        Returns:
            List of Transaction objects parsed from the PDF

        Raises:
            ValueError: If the response cannot be parsed
            Exception: For other errors during parsing
        """
        try:
            logger.info(f"Parsing PDF document ({len(pdf_data)} bytes) with multimodal input")

            # Get system and user prompts
            system_prompt = get_system_prompt()
            user_prompt = get_user_prompt()

            # Call the LLM with PDF document
            response = self.bedrock_client.invoke_with_document(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                pdf_data=pdf_data,
                enable_caching=self.enable_caching,
            )

            # Parse the response into Transaction objects
            transactions = ResponseParser.parse_transactions(response)

            logger.info(f"Successfully parsed {len(transactions)} transactions")
            return transactions

        except Exception as e:
            logger.error(f"Error parsing transactions with LLM: {e}")
            raise
