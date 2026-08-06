import random

AMOUNT_RANGE = {

    "Food": (8, 35),

    "Shopping": (30, 500),

    "Travel": (10, 120),

    "Fuel": (40, 90),

    "Entertainment": (8, 35),

    "Bills": (80, 300),

    "Healthcare": (30, 250),

    "Investment": (200, 1500)

}

PAYMENT_METHODS = [
    "Credit Card",
    "Debit Card",
    "UPI",
    "Bank Transfer"
]

def random_amount(category):
    low, high = AMOUNT_RANGE[category]
    return round(random.uniform(low, high), 2)

def payment_method():
    return random.choice(PAYMENT_METHODS)
