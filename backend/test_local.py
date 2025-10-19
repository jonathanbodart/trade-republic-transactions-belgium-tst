"""
Quick test script to verify the PDF parser works locally
Run: python test_local.py
"""
import sys
from pathlib import Path
from src.parsers import PDFParser, LLMParser
from src.utils import aggregate_transactions

def main():
    pdf_path = "/Users/jonathanbodart/Desktop/Account statement.pdf"

    if not Path(pdf_path).exists():
        print(f"Error: PDF not found at {pdf_path}")
        print("Please update the path in test_local.py")
        return

    print("=" * 60)
    print("Transaction Parser - Local Test")
    print("=" * 60)

    # Step 1: Extract text from PDF
    print("\n[1/3] Extracting text from PDF...")
    with open(pdf_path, 'rb') as f:
        text = PDFParser.extract_text(f)

    print(f"✓ Extracted {len(text):,} characters from PDF")
    print(f"✓ First 200 chars: {text[:200]}...")

    # Step 2: Parse with LLM
    print("\n[2/3] Parsing transactions with AWS Bedrock (Claude)...")
    print("Note: This requires AWS credentials and Bedrock access")

    try:
        llm = LLMParser(region_name="us-east-1")
        transactions = llm.parse_transactions(text)

        print(f"✓ Successfully parsed {len(transactions)} transactions")

        # Step 3: Display results
        print("\n[3/3] Parsed Transactions:")
        print("-" * 60)

        for i, txn in enumerate(transactions[:10], 1):  # Show first 10
            print(f"{i:2}. {txn.date} | {txn.isin:15} | {txn.transaction_type:8} | €{float(txn.amount_euros):8.2f} | {txn.product_name[:40]}")

        if len(transactions) > 10:
            print(f"... and {len(transactions - 10)} more transactions")

        # Aggregated view
        print("\n" + "=" * 60)
        print("Aggregated by ISIN:")
        print("-" * 60)

        aggregated = aggregate_transactions(transactions)

        for agg in aggregated[:5]:  # Show first 5
            print(f"{agg.isin:15} | {agg.transaction_type:8} | Qty: {float(agg.total_quantity):10.6f} | Total: €{float(agg.total_amount_euros):8.2f} | ({agg.transaction_count} txns)")

        print("\n✓ Test completed successfully!")
        print(f"\nTotal: {len(transactions)} transactions, {len(aggregated)} aggregated groups")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure you have:")
        print("1. AWS credentials configured (run 'aws configure')")
        print("2. Access to Bedrock enabled in your AWS account")
        print("3. Requested access to Claude 3.5 Sonnet in Bedrock console")
        sys.exit(1)

if __name__ == "__main__":
    main()
