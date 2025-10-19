"""
Prompt templates for LLM-based transaction parsing.

This module contains all prompt templates used by the LLM parser,
keeping them separate from business logic for better maintainability.
"""

TRANSACTION_PARSING_PROMPT = """You are a financial transaction parser. Extract all financial transactions from the following bank statement text.

For each transaction, extract:
- date: The transaction date (keep in format like "02 Sep 2025")
- isin: The ISIN code (e.g., IE00B5BMR087, XF000BTC0017 for Bitcoin, US92826C8394 for stocks)
- product_name: The full product name
- quantity: The number of shares/units (use the exact decimal number provided)
- amount_euros: The amount in euros (from MONEY IN or MONEY OUT column)
- transaction_type: Either "BUY", "SELL", or "DIVIDEND"

Rules:
1. For "Trade" type with "Savings plan execution" or regular trades with MONEY OUT → transaction_type = "BUY"
2. For "Trade" type with "Sell trade" and MONEY IN → transaction_type = "SELL"
3. For "Earnings" type with "Cash Dividend" → transaction_type = "DIVIDEND" (quantity should be 0)
4. Ignore "Interest Payment" transactions
5. Extract the ISIN from the description text (it's usually after the transaction type and before the product name)
6. For dividends, the ISIN comes after "for ISIN"
7. Use exact decimal values for quantity and amount

Return ONLY a valid JSON array of transactions, with no additional text or explanation.

Example output format:
[
  {{
    "date": "02 Sep 2025",
    "isin": "IE00B5BMR087",
    "product_name": "iShares VII plc - iShares Core S&P 500 UCITS ETF USD (Acc)",
    "quantity": "0.085178",
    "amount_euros": "50.00",
    "transaction_type": "BUY"
  }},
  {{
    "date": "29 Sep 2025",
    "isin": "IE00B3WJKG14",
    "product_name": "iShares V plc - iShares S&P 500 Information Technology Sector UCITS ETF USD (Acc)",
    "quantity": "62.149257",
    "amount_euros": "2173.20",
    "transaction_type": "SELL"
  }},
  {{
    "date": "02 Sep 2025",
    "isin": "US92826C8394",
    "product_name": "VISA",
    "quantity": "0",
    "amount_euros": "1.66",
    "transaction_type": "DIVIDEND"
  }}
]

Bank statement text:
{pdf_text}
"""


def build_parsing_prompt(pdf_text: str) -> str:
    """
    Build the prompt for transaction parsing.

    Args:
        pdf_text: Extracted text from PDF

    Returns:
        Formatted prompt string ready for LLM
    """
    return TRANSACTION_PARSING_PROMPT.format(pdf_text=pdf_text)
