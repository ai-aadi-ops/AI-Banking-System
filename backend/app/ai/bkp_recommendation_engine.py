OFFERS = {
    "Electronics": {
        "merchant": "Apple Store",
        "product": "MacBook Air M4",
        "price": 1799,
        "discount": "12%",
        "interest": 6.5,
        "months": 12
    },
    "Shopping": {
        "merchant": "Amazon",
        "product": "Amazon Premium Bundle",
        "price": 899,
        "discount": "15%",
        "interest": 5.9,
        "months": 6
    },
    "Travel": {
        "merchant": "Delta Airlines",
        "product": "International Flight Voucher",
        "price": 1200,
        "discount": "8%",
        "interest": 4.9,
        "months": 9
    },
    "Food": {
        "merchant": "DoorDash",
        "product": "Food Subscription",
        "price": 299,
        "discount": "20%",
        "interest": 0,
        "months": 3
    }
}

IGNORE = {
    "Housing",
    "Salary",
    "Insurance",
    "Utilities",
    "Internet",
    "Healthcare",
    "Fuel"
}


def generate_recommendation(
    spending,
    financial_health,
    account,
    card
):

    category = spending["highest_spending_category"]

    if category in IGNORE:
        category = "Electronics"

    offer = OFFERS.get(category, OFFERS["Shopping"])

    emi = round(
        offer["price"] / offer["months"],
        2
    )

    return {
        "recommended_category": category,
        "merchant": offer["merchant"],
        "product": offer["product"],
        "price": offer["price"],
        "discount": offer["discount"],
        "interest_rate": offer["interest"],
        "emi_monthly": emi,
        "financial_health":
            financial_health["financial_health_score"],
        "status":
            financial_health["status"],
        "available_balance":
            float(account.balance),
        "available_savings":
            float(account.savings),
        "card":
            card.card_type,
        "card_number":
            "************" + card.card_number[-4:]
    }
