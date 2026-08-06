import psycopg2

from seed_data import all_transactions

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="banking_ai",
    user="postgres",
    password="Robert@123"
)

cur = conn.cursor()

# Purana data delete karo
cur.execute("DELETE FROM bank_transactions;")

# Naya data insert karo
for txn in all_transactions:

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
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
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

conn.commit()

print(f"Inserted {len(all_transactions)} transactions.")

cur.close()
conn.close()
