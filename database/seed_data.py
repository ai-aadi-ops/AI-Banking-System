import random
import uuid
import psycopg2
CITIES = [
    "Noida",
    "Gurugram",
    "Delhi",
    "Jaipur",
    "Mumbai"
]

DEVICES = [
    "Android",
    "iPhone",
    "Web"
]

CHANNELS = [
    "UPI",
    "Debit Card",
    "Credit Card",
    "Net Banking"
]

from datetime import datetime, timedelta
STARTING_BALANCE = 20000.00
balance = STARTING_BALANCE
from merchants import MERCHANTS
from categories import CATEGORIES
from utils import random_amount, payment_method
from generators import (
    add_coffee,
    add_lunch,
    add_fuel,
    add_grocery,
    add_netflix
)
def generate_transactions(current_date):

    transactions = []

    # Salary - Every Month 1st
    if current_date.day == 1:

        transactions.append({
            "merchant": "Employer Payroll",
            "category": "Salary",
            "amount": 6500,
            "type": "Credit",
            "method": "Bank Transfer"
        })

    # Rent - Every Month 3rd
    if current_date.day == 3:

        transactions.append({
            "merchant": "Apartment Rent",
            "category": "Rent",
            "amount": 1800,
            "type": "Debit",
            "method": "Bank Transfer"
        })

    # Electricity - Every Month 8th
    if current_date.day == 8:

        transactions.append({
            "merchant": "Electricity",
            "category": "Bills",
            "amount": random.randint(120,160),
            "type": "Debit",
            "method": "Bank Transfer"
        })

    # Other rules
    add_coffee(current_date, transactions)
    add_lunch(current_date, transactions)
    add_fuel(current_date, transactions)
    add_grocery(current_date, transactions)
    add_netflix(current_date, transactions)
    
    return transactions

def get_connection():

    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="banking_ai",
        user="postgres",
        password="Robert@123"
    )

def insert_transaction(cur, txn):

    cur.execute(
        """
        INSERT INTO bank_transactions
        (
            customer_id,
            merchant_name,
            category,
            amount,
            transaction_type,
            payment_method,
            transaction_date,
            ai_score
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            1,
            txn["merchant"],
            txn["category"],
            txn["amount"],
            txn["type"],
            txn["method"],
            txn["date"],
            str(txn["risk_score"])
        )
    )

def update_balance(current_date, transactions):

    global balance

    for txn in transactions:

        if txn["type"] == "Credit":
            balance += txn["amount"]
        else:
            balance -= txn["amount"]

        txn["balance"] = round(balance, 2)
        
        txn["transaction_id"] = str(uuid.uuid4())[:12].upper()
        txn["date"] = current_date.strftime("%Y-%m-%d")
        txn["time"] = f"{random.randint(8,22):02}:{random.randint(0,59):02}:{random.randint(0,59):02}"
        txn["status"] = "SUCCESS"
        txn["currency"] = "USD"

        txn["city"] = random.choice(CITIES)
        txn["device"] = random.choice(DEVICES)
        txn["channel"] = random.choice(CHANNELS)
        txn["reward_points"] = int(txn["amount"] // 5)
        txn["cashback"] = round(txn["amount"] * 0.01, 2)
        txn["risk_score"] = random.randint(1, 10)

    return transactions

START_DATE = datetime(2026, 2, 6)
END_DATE = datetime(2026, 8, 5)

current_date = START_DATE

all_transactions = []

while current_date <= END_DATE:

    transactions = generate_transactions(current_date)

    transactions = update_balance(current_date, transactions)

    all_transactions.extend(transactions)

    current_date += timedelta(days=1)

print(f"\nGenerated {len(all_transactions)} transactions.")
