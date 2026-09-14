import random
import uuid
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import Customer, Account, Card, Transaction, User

def generate_demo_transactions(start_date=datetime(2026, 2, 1), end_date=datetime(2026, 9, 14)):
    """Generate deterministic, realistic demo transactions for Robert Wilson."""
    random.seed(42)  # For reproducible demo numbers
    current_date = start_date
    transactions = []

    while current_date <= end_date:
        d = current_date.date()

        # 1. Monthly Salary (1st of month)
        if current_date.day == 1:
            transactions.append({
                "merchant_name": "Employer Payroll",
                "category": "Salary",
                "amount": 6500.00,
                "transaction_type": "Credit",
                "payment_method": "Bank Transfer",
                "transaction_date": d,
                "ai_score": "1"
            })

        # 2. Apartment Rent (3rd of month)
        if current_date.day == 3:
            transactions.append({
                "merchant_name": "Apartment Rent",
                "category": "Rent",
                "amount": 1800.00,
                "transaction_type": "Debit",
                "payment_method": "Bank Transfer",
                "transaction_date": d,
                "ai_score": "1"
            })

        # 3. Electricity Bill (8th of month)
        if current_date.day == 8:
            transactions.append({
                "merchant_name": "Electricity",
                "category": "Bills",
                "amount": round(float(random.randint(120, 160)), 2),
                "transaction_type": "Debit",
                "payment_method": "Bank Transfer",
                "transaction_date": d,
                "ai_score": "1"
            })

        # 4. Netflix Subscription (15th of month)
        if current_date.day == 15:
            transactions.append({
                "merchant_name": "Netflix",
                "category": "Entertainment",
                "amount": 18.99,
                "transaction_type": "Debit",
                "payment_method": "Credit Card",
                "transaction_date": d,
                "ai_score": "1"
            })

        # 5. Electronics / Tech purchase (20th of every second month)
        if current_date.day == 20 and current_date.month % 2 == 0:
            transactions.append({
                "merchant_name": "Best Buy",
                "category": "Electronics",
                "amount": round(random.uniform(250.0, 450.0), 2),
                "transaction_type": "Debit",
                "payment_method": "Credit Card",
                "transaction_date": d,
                "ai_score": "3"
            })

        # 6. Coffee (Weekdays)
        if current_date.weekday() < 5:
            transactions.append({
                "merchant_name": "Starbucks",
                "category": "Food",
                "amount": round(random.uniform(5.50, 11.50), 2),
                "transaction_type": "Debit",
                "payment_method": "Credit Card",
                "transaction_date": d,
                "ai_score": str(random.randint(1, 4))
            })

        # 7. Lunch (Weekdays)
        if current_date.weekday() < 5:
            lunch_merchant = random.choice(["Subway", "McDonald's", "Chipotle"])
            transactions.append({
                "merchant_name": lunch_merchant,
                "category": "Food",
                "amount": round(random.uniform(12.00, 24.00), 2),
                "transaction_type": "Debit",
                "payment_method": "Credit Card",
                "transaction_date": d,
                "ai_score": str(random.randint(1, 4))
            })

        # 8. Fuel (Every 5th day)
        if current_date.day % 5 == 0:
            transactions.append({
                "merchant_name": "Shell",
                "category": "Fuel",
                "amount": round(random.uniform(45.00, 78.00), 2),
                "transaction_type": "Debit",
                "payment_method": "Credit Card",
                "transaction_date": d,
                "ai_score": str(random.randint(1, 3))
            })

        # 9. Groceries (Every Sunday)
        if current_date.weekday() == 6:
            transactions.append({
                "merchant_name": "Walmart",
                "category": "Groceries",
                "amount": round(random.uniform(95.00, 210.00), 2),
                "transaction_type": "Debit",
                "payment_method": "Debit Card",
                "transaction_date": d,
                "ai_score": str(random.randint(1, 3))
            })

        current_date += timedelta(days=1)

    return transactions


def reset_postgres_sequences(db: Session):
    """Safely reset PostgreSQL auto-increment sequences if on PostgreSQL."""
    try:
        tables = [
            ("customers", "customer_id"),
            ("accounts", "account_id"),
            ("cards", "card_id"),
            ("bank_transactions", "transaction_id"),
            ("users", "id"),
        ]
        for table, col in tables:
            try:
                db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', '{col}'), COALESCE((SELECT MAX({col}) FROM {table}), 1));"))
            except Exception:
                pass
        db.commit()
    except Exception:
        db.rollback()


def seed_database(db: Session, force: bool = False):
    """
    Seed initial Customer, Account, Card, User, and Bank Transactions.
    If force=False, only seeds if Customer table is empty.
    """
    customer_exists = db.query(Customer).filter(Customer.customer_id == 1).first()

    if customer_exists and not force:
        # Check if transactions exist
        txn_count = db.query(Transaction).filter(Transaction.customer_id == 1).count()
        if txn_count > 0:
            return {
                "status": "already_seeded",
                "message": "Database already contains customer and transaction data.",
                "customer_id": 1,
                "transactions_count": txn_count
            }

    # 1. Clean existing records if forcing re-seed
    if force:
        try:
            db.query(Transaction).delete()
            db.query(Card).delete()
            db.query(Account).delete()
            db.query(User).delete()
            db.query(Customer).delete()
            db.commit()
        except Exception:
            db.rollback()

    # 2. Seed Customer: Robert Wilson
    customer = db.query(Customer).filter(Customer.customer_id == 1).first()
    if not customer:
        customer = Customer(
            customer_id=1,
            customer_code="CUST001",
            full_name="Robert Wilson",
            email="robert.wilson@demo.com",
            phone="+1-555-0199",
            salary=6500.00,
            customer_since=date(2023, 1, 15),
            kyc_status="VERIFIED"
        )
        db.add(customer)
        db.flush()

    # 3. Seed Account: Savings account with $20,000 balance
    account = db.query(Account).filter(Account.customer_id == 1).first()
    if not account:
        account = Account(
            account_id=1,
            customer_id=1,
            account_number="ACC-98234101",
            account_type="Savings",
            balance=20000.00,
            savings=5000.00,
            monthly_salary=6500.00,
            status="ACTIVE"
        )
        db.add(account)
        db.flush()

    # 4. Seed Card
    card = db.query(Card).filter(Card.customer_id == 1).first()
    if not card:
        card = Card(
            card_id=1,
            customer_id=1,
            card_number="4532-8821-9934-1209",
            expiry_date="12/28",
            cvv="342",
            card_type="Visa Platinum",
            status="ACTIVE"
        )
        db.add(card)
        db.flush()

    # 5. Seed User for auth/login
    user = db.query(User).filter(User.email == "robert.wilson@demo.com").first()
    if not user:
        user = User(
            id=1,
            full_name="Robert Wilson",
            email="robert.wilson@demo.com",
            password_hash="demo_password_hash_2026",
            role="customer",
            is_active="true"
        )
        db.add(user)
        db.flush()

    # 6. Seed Bank Transactions
    existing_txns = db.query(Transaction).filter(Transaction.customer_id == 1).count()
    if existing_txns == 0:
        raw_txns = generate_demo_transactions()
        for t in raw_txns:
            txn = Transaction(
                customer_id=1,
                merchant_name=t["merchant_name"],
                category=t["category"],
                amount=t["amount"],
                transaction_type=t["transaction_type"],
                payment_method=t["payment_method"],
                transaction_date=t["transaction_date"],
                ai_score=t["ai_score"]
            )
            db.add(txn)
        db.flush()

    db.commit()

    reset_postgres_sequences(db)

    total_txns = db.query(Transaction).filter(Transaction.customer_id == 1).count()

    return {
        "status": "success",
        "message": "Demo data successfully seeded!",
        "customer": {
            "id": customer.customer_id,
            "name": customer.full_name,
            "salary": float(customer.salary)
        },
        "account": {
            "balance": float(account.balance),
            "savings": float(account.savings),
            "monthly_salary": float(account.monthly_salary)
        },
        "transactions_seeded": total_txns
    }


def seed_database_if_empty(db: Session):
    """Helper called on application startup to ensure tables are never left empty."""
    try:
        count = db.query(Customer).count()
        if count == 0:
            print("Database is empty. Automatically seeding demo banking data...")
            result = seed_database(db, force=False)
            print(f"Auto-seeding complete: {result.get('message')}, Transactions: {result.get('transactions_seeded')}")
        else:
            # Check if account exists
            acc_count = db.query(Account).count()
            txn_count = db.query(Transaction).count()
            if acc_count == 0 or txn_count == 0:
                print("Missing account or transactions. Running seeder...")
                seed_database(db, force=False)
    except Exception as e:
        print(f"Auto-seeding warning/error: {e}")
        try:
            db.rollback()
        except Exception:
            pass
