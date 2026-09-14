import random
import uuid
import psycopg2
import os

def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "banking_ai"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "Robert@123")
    )

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

if __name__ == "__main__":
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # 1. Ensure Customer 1 exists
        cur.execute("""
            INSERT INTO customers (customer_id, customer_code, full_name, email, phone, salary, customer_since, kyc_status)
            VALUES (1, 'CUST001', 'Robert Wilson', 'robert.wilson@demo.com', '+1-555-0199', 6500.00, '2023-01-15', 'VERIFIED')
            ON CONFLICT (customer_id) DO NOTHING;
        """)

        # 2. Ensure Account 1 exists
        cur.execute("""
            INSERT INTO accounts (account_id, customer_id, account_number, account_type, balance, savings, monthly_salary, status)
            VALUES (1, 1, 'ACC-98234101', 'Savings', 20000.00, 5000.00, 6500.00, 'ACTIVE')
            ON CONFLICT (account_id) DO NOTHING;
        """)

        # 3. Ensure Card 1 exists
        cur.execute("""
            INSERT INTO cards (card_id, customer_id, card_number, expiry_date, cvv, card_type, status)
            VALUES (1, 1, '4532-8821-9934-1209', '12/28', '342', 'Visa Platinum', 'ACTIVE')
            ON CONFLICT (card_id) DO NOTHING;
        """)

        # 4. Clean old transactions and insert new ones
        cur.execute("DELETE FROM bank_transactions WHERE customer_id = 1;")
        for txn in all_transactions:
            insert_transaction(cur, txn)

        conn.commit()
        print(f"Inserted {len(all_transactions)} transactions into PostgreSQL.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Database error:", e)
        raise
    finally:
        if conn:
            conn.close()
