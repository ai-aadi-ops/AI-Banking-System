import random


def add_coffee(current_date, transactions):

    if current_date.weekday() < 5:

        transactions.append({
            "merchant": "Starbucks",
            "category": "Food",
            "amount": round(random.uniform(5, 12), 2),
            "type": "Debit",
            "method": "Credit Card"
        })


def add_lunch(current_date, transactions):

    if current_date.weekday() < 5:

        transactions.append({
            "merchant": random.choice([
                "Subway",
                "McDonald's",
                "Chipotle"
            ]),
            "category": "Food",
            "amount": round(random.uniform(12, 25), 2),
            "type": "Debit",
            "method": "Credit Card"
        })


def add_fuel(current_date, transactions):

    if current_date.day % 5 == 0:

        transactions.append({
            "merchant": "Shell",
            "category": "Fuel",
            "amount": round(random.uniform(45, 80), 2),
            "type": "Debit",
            "method": "Credit Card"
        })


def add_grocery(current_date, transactions):

    if current_date.weekday() == 6:

        transactions.append({
            "merchant": "Walmart",
            "category": "Groceries",
            "amount": round(random.uniform(90, 220), 2),
            "type": "Debit",
            "method": "Debit Card"
        })


def add_netflix(current_date, transactions):

    if current_date.day == 15:

        transactions.append({
            "merchant": "Netflix",
            "category": "Entertainment",
            "amount": 18.99,
            "type": "Debit",
            "method": "Credit Card"
        })
