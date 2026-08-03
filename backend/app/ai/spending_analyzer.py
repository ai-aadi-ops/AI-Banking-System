from collections import defaultdict


def analyze_transactions(transactions):
    category_total = defaultdict(float)
    merchant_total = defaultdict(float)

    total_spent = 0

    for tx in transactions:

        if tx.transaction_type.lower() != "debit":
            continue

        amount = float(tx.amount)

        total_spent += amount

        category_total[tx.category] += amount
        merchant_total[tx.merchant_name] += amount

    highest_category = max(
        category_total,
        key=category_total.get,
        default="None"
    )

    highest_merchant = max(
        merchant_total,
        key=merchant_total.get,
        default="None"
    )

    return {

        "total_spent": round(total_spent, 2),

        "highest_spending_category": highest_category,

        "highest_category_amount":
            round(category_total.get(highest_category, 0), 2),

        "favorite_merchant": highest_merchant,

        "merchant_spending":
            round(merchant_total.get(highest_merchant, 0), 2),

        "category_breakdown": {
            k: round(v, 2)
            for k, v in category_total.items()
            }
    }
