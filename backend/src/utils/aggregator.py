from collections import defaultdict
from decimal import Decimal
from typing import Literal

from ..models.transaction import Transaction, AggregatedTransaction


def aggregate_transactions(transactions: list[Transaction]) -> list[AggregatedTransaction]:
    """
    Aggregate transactions by ISIN and transaction type

    Args:
        transactions: List of individual transactions

    Returns:
        List of aggregated transactions
    """
    # Group by (ISIN, transaction_type)
    grouped = defaultdict(lambda: {
        "product_name": "",
        "total_quantity": Decimal("0"),
        "total_amount_euros": Decimal("0"),
        "count": 0
    })

    for txn in transactions:
        key = (txn.isin, txn.transaction_type)

        grouped[key]["product_name"] = txn.product_name
        grouped[key]["total_quantity"] += txn.quantity
        grouped[key]["total_amount_euros"] += txn.amount_euros
        grouped[key]["count"] += 1

    # Convert to AggregatedTransaction objects
    aggregated = []
    for (isin, txn_type), data in grouped.items():
        aggregated.append(
            AggregatedTransaction(
                isin=isin,
                product_name=data["product_name"],
                total_quantity=data["total_quantity"],
                total_amount_euros=data["total_amount_euros"],
                transaction_type=txn_type,
                transaction_count=data["count"]
            )
        )

    # Sort by ISIN and transaction type
    aggregated.sort(key=lambda x: (x.isin, x.transaction_type))

    return aggregated
