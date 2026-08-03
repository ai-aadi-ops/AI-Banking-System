def purchase_decision(
    recommendation,
    account,
    financial_health
):

    balance = float(account.balance)

    savings = float(account.savings)

    price = float(recommendation["price"])

    emi = float(recommendation["emi_monthly"])

    remaining_balance = balance - price

    freeze_amount = emi

    if financial_health["financial_health_score"] >= 75:

        decision = "APPROVED"

    else:

        decision = "REVIEW REQUIRED"

    return {

        "decision": decision,

        "product": recommendation["product"],

        "purchase_price": price,

        "current_balance": balance,

        "remaining_balance": round(
            remaining_balance,
            2
        ),

        "available_savings": savings,

        "monthly_emi": emi,

        "freeze_next_month": freeze_amount,

        "interest_rate":
            recommendation["interest_rate"],

        "payment_mode": "Bank EMI",

        "cashback":
            recommendation["discount"]
    }
