from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.ai.spending_analyzer import analyze_transactions
from app.database import get_db
from app.ai.recommendation_engine import generate_recommendation
from app.ai.spending_analyzer import analyze_transactions
from app.ai.financial_health import calculate_financial_health
from app.ai.purchase_decision import purchase_decision
from app.services.purchase_service import PurchaseService
from app.ai.financial_advisor import generate_financial_advice
from app.ai.chat_service import chat_with_ai
from app.database import engine
from app.models import Base
from sqlalchemy import func
from app.models import Account, Transaction
from fastapi.middleware.cors import CORSMiddleware
from app.ai.recommendation_engine import generate_recommendation
from app.models import (
    Customer,
    Account,
    Card,
    Transaction,
    Recommendation,
    Loan,
)

app = FastAPI(title="AI Banking Demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {
        "message": "AI Banking Backend Running"
    }


@app.get("/customers")
def customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()


@app.get("/accounts")
def accounts(db: Session = Depends(get_db)):
    return db.query(Account).all()


@app.get("/cards")
def cards(db: Session = Depends(get_db)):
    return db.query(Card).all()


@app.get("/transactions")
def transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()


@app.get("/recommendations")
def recommendations(db: Session = Depends(get_db)):
    return db.query(Recommendation).all()


@app.get("/loans")
def loans(db: Session = Depends(get_db)):
    return db.query(Loan).all()

@app.get("/ai/analyze/{customer_id}")
def analyze(customer_id: int,
            db: Session = Depends(get_db)):

    transactions = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .all()
    )

    return analyze_transactions(transactions)

@app.get("/ai/financial-health/{customer_id}")
def financial_health(customer_id: int,
                     db: Session = Depends(get_db)):

    customer = (
        db.query(Customer)
        .filter(Customer.customer_id == customer_id)
        .first()
    )

    account = (
        db.query(Account)
        .filter(Account.customer_id == customer_id)
        .first()
    )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .all()
    )

    if not customer or not account:
        return {"error": "Customer not found"}

    return calculate_financial_health(
        customer,
        account,
        transactions
    )
@app.get("/ai/recommendation/{customer_id}")
def recommendation(customer_id: int,
                   db: Session = Depends(get_db)):

    customer = (
        db.query(Customer)
        .filter(Customer.customer_id == customer_id)
        .first()
    )

    account = (
        db.query(Account)
        .filter(Account.customer_id == customer_id)
        .first()
    )

    card = (
        db.query(Card)
        .filter(Card.customer_id == customer_id)
        .first()
    )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .all()
    )

    if not customer or not account or not card:
        return {"error": "Customer not found"}

    spending = analyze_transactions(transactions)

    health = calculate_financial_health(
        customer,
        account,
        transactions
    )

    return generate_recommendation(
        spending,
        health,
        account,
        card
    )
@app.get("/ai/purchase/{customer_id}")

def purchase(
    customer_id:int,
    db:Session=Depends(get_db)
):

    customer=db.query(Customer).filter(
        Customer.customer_id==customer_id
    ).first()

    account=db.query(Account).filter(
        Account.customer_id==customer_id
    ).first()

    card=db.query(Card).filter(
        Card.customer_id==customer_id
    ).first()

    transactions=db.query(Transaction).filter(
        Transaction.customer_id==customer_id
    ).all()

    spending=analyze_transactions(
        transactions
    )

    health=calculate_financial_health(
        customer,
        account,
        transactions
    )

    recommendation=generate_recommendation(
        spending,
        health,
        account,
        card
    )

    decision = purchase_decision(
        recommendation,
        account,
        health
    )

    purchase_service = PurchaseService(db)

    result = purchase_service.execute_purchase(
        customer_id=customer_id,
        recommendation=recommendation,
        decision=decision,
        account=account,
        )

    return {
        **decision,
        **result
    }

@app.get("/ai/advisor/{customer_id}")
def advisor(
    customer_id: int,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(Customer.customer_id == customer_id)
        .first()
    )

    account = (
        db.query(Account)
        .filter(Account.customer_id == customer_id)
        .first()
    )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .all()
    )

    if not customer or not account:
        return {"error": "Customer not found"}

    spending = analyze_transactions(
        transactions
    )

    health = calculate_financial_health(
        customer,
        account,
        transactions
    )

    advice = generate_financial_advice(
        customer,
        account,
        spending,
        health
    )

    return {
        "customer": customer.full_name,
        "financial_advice": advice
    }
from fastapi import Body


@app.post("/ai/chat/{customer_id}")
def ai_chat(
    customer_id: int,
    body: dict = Body(...),
    db: Session = Depends(get_db),
):

    customer = (
        db.query(Customer)
        .filter(Customer.customer_id == customer_id)
        .first()
    )

    account = (
        db.query(Account)
        .filter(Account.customer_id == customer_id)
        .first()
    )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .all()
    )

    spending = analyze_transactions(transactions)

    health = calculate_financial_health(
        customer,
        account,
        transactions,
    )

    answer = chat_with_ai(
        customer,
        account,
        spending,
        health,
        body["question"],
    )

    return {
        "customer": customer.full_name,
        "question": body["question"],
        "answer": answer,
    }
@app.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):

    account = db.query(Account).first()

    if not account:
        return {
            "balance": 0,
            "income": 0,
            "expenses": 0,
            "savings": 0
        }

    expenses = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.transaction_type == "Debit")
        .scalar()
    ) or 0

    return {
        "balance": float(account.balance),
        "income": float(account.monthly_salary),
        "expenses": float(expenses),
        "savings": float(account.savings)
    }
