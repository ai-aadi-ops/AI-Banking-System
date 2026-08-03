from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Numeric, Date, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(20), unique=True)
    full_name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    salary = Column(Numeric(12, 2))
    customer_since = Column(Date)
    kyc_status = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    account_number = Column(String(20))
    account_type = Column(String(20))
    balance = Column(Numeric(12, 2))
    savings = Column(Numeric(12, 2))
    monthly_salary = Column(Numeric(12, 2))
    status = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())


class Card(Base):
    __tablename__ = "cards"

    card_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    card_number = Column(String(25))
    expiry_date = Column(String(10))
    cvv = Column(String(5))
    card_type = Column(String(20))
    status = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())


class Transaction(Base):
    __tablename__ = "bank_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    merchant_name = Column(String(100))
    category = Column(String(50))
    amount = Column(Numeric(12, 2))
    transaction_type = Column(String(20))
    payment_method = Column(String(20))
    transaction_date = Column(Date)
    ai_score = Column(String(20))


class Recommendation(Base):
    __tablename__ = "ai_recommendations"

    recommendation_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    merchant_name = Column(String(100))
    recommended_product = Column(String(200))
    original_price = Column(Numeric(12, 2))
    discounted_price = Column(Numeric(12, 2))
    emi_amount = Column(Numeric(12, 2))
    confidence_score = Column(Numeric(5, 2))
    reason = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Loan(Base):
    __tablename__ = "loans"

    loan_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    principal_amount = Column(Numeric(12, 2))
    interest_rate = Column(Numeric(5, 2))
    tenure_months = Column(Integer)
    emi = Column(Numeric(12, 2))
    frozen_amount = Column(Numeric(12, 2))
    status = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())
