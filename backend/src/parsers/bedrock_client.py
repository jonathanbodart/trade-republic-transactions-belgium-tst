"""
AWS Bedrock client wrapper for LLM interactions.

This module provides a clean interface to AWS Bedrock API,
handling request/response formatting and error handling.
Supports system prompts, multimodal inputs (PDFs), and prompt caching.
"""

import base64
import json
import logging
from typing import Any, Dict, List

import boto3

logger = logging.getLogger(__name__)


class BedrockClient:
    """Wrapper for AWS Bedrock Runtime API with multimodal and caching support"""

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

    def invoke_with_document(
        self,
        system_prompt: str,
        user_prompt: str,
        pdf_data: bytes,
        enable_caching: bool = True,
    ) -> str:
        """
        Invoke the Bedrock model with a PDF document and prompts.

        Args:
            system_prompt: System-level instructions (will be cached if enabled)
            user_prompt: User message text
            pdf_data: PDF file content as bytes
            enable_caching: Whether to enable prompt caching for system prompt

        Returns:
            The text response from the model

        Raises:
            ValueError: If the response format is invalid
            Exception: For other API errors
        """
        request_body = self._build_multimodal_request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            pdf_data=pdf_data,
            enable_caching=enable_caching,
        )

        logger.debug(f"Invoking Bedrock model {self.model_id} with PDF document")

        try:
            response = self.client.invoke_model(
                modelId=self.model_id, body=json.dumps(request_body)
            )

            response_body = json.loads(response["body"].read())

            # Log cache usage if available
            if "usage" in response_body:
                usage = response_body["usage"]
                logger.info(
                    f"Token usage - Input: {usage.get('input_tokens', 0)}, "
                    f"Cache creation: {usage.get('cache_creation_input_tokens', 0)}, "
                    f"Cache read: {usage.get('cache_read_input_tokens', 0)}, "
                    f"Output: {usage.get('output_tokens', 0)}"
                )

            return self._extract_text_from_response(response_body)

        except Exception as e:
            logger.error(f"Error invoking Bedrock model: {e}")
            raise

    def _build_multimodal_request(
        self,
        system_prompt: str,
        user_prompt: str,
        pdf_data: bytes,
        enable_caching: bool,
    ) -> Dict[str, Any]:
        """
        Build request body with system prompt, user prompt, and PDF document.

        Args:
            system_prompt: System-level instructions
            user_prompt: User message
            pdf_data: PDF file bytes
            enable_caching: Whether to enable caching for system prompt

        Returns:
            Request body dictionary
        """
        # System message with optional caching
        system_content: List[Dict[str, Any]] = [
            {
                "type": "text",
                "text": system_prompt,
            }
        ]

        # Add cache control to system prompt if enabled
        if enable_caching:
            system_content[0]["cache_control"] = {"type": "ephemeral"}

        # Encode PDF as base64
        pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")

        # User message with PDF document and text
        user_content: List[Dict[str, Any]] = [
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": pdf_base64,
                },
            },
            {
                "type": "text",
                "text": user_prompt,
            },
        ]

        return {
            "anthropic_version": self.ANTHROPIC_VERSION,
            "max_tokens": self.max_tokens,
            "system": system_content,
            "messages": [{"role": "user", "content": user_content}],
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
