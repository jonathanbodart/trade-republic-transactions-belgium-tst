"""
AWS Bedrock client wrapper for LLM interactions.

This module provides a clean interface to AWS Bedrock API,
handling request/response formatting and error handling.
"""

import json
import logging
from typing import Any, Dict

import boto3

logger = logging.getLogger(__name__)


class BedrockClient:
    """Wrapper for AWS Bedrock Runtime API"""

    # Default model configuration
    DEFAULT_REGION = "eu-west-1"
    DEFAULT_MODEL_ID = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
    DEFAULT_MAX_TOKENS = 4000
    DEFAULT_TEMPERATURE = 0.0  # Deterministic for parsing
    ANTHROPIC_VERSION = "bedrock-2023-05-31"

    def __init__(
        self,
        region_name: str = DEFAULT_REGION,
        model_id: str = DEFAULT_MODEL_ID,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ):
        """
        Initialize the Bedrock client.

        Args:
            region_name: AWS region for Bedrock service
            model_id: Claude model ID or inference profile to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for response generation (0.0 = deterministic)
        """
        self.client = boto3.client("bedrock-runtime", region_name=region_name)
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        logger.info(
            f"Initialized Bedrock client with model {model_id} in region {region_name}"
        )

    def invoke(self, prompt: str) -> str:
        """
        Invoke the Bedrock model with a prompt.

        Args:
            prompt: The input prompt for the model

        Returns:
            The text response from the model

        Raises:
            ValueError: If the response format is invalid
            Exception: For other API errors
        """
        request_body = self._build_request_body(prompt)

        logger.debug(f"Invoking Bedrock model {self.model_id}")

        try:
            response = self.client.invoke_model(
                modelId=self.model_id, body=json.dumps(request_body)
            )

            response_body = json.loads(response["body"].read())
            return self._extract_text_from_response(response_body)

        except Exception as e:
            logger.error(f"Error invoking Bedrock model: {e}")
            raise

    def _build_request_body(self, prompt: str) -> Dict[str, Any]:
        """Build the request body for Bedrock API"""
        return {
            "anthropic_version": self.ANTHROPIC_VERSION,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
        }

    def _extract_text_from_response(self, response_body: Dict[str, Any]) -> str:
        """
        Extract text content from Bedrock response.

        Args:
            response_body: The parsed JSON response from Bedrock

        Returns:
            The text content from the response

        Raises:
            ValueError: If no content is found in the response
        """
        content = response_body.get("content", [])
        if content and len(content) > 0:
            text = content[0].get("text", "")
            if text:
                return text

        logger.error(f"Invalid response structure: {response_body}")
        raise ValueError("No content in Bedrock response")
