from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import hashlib
import secrets
import random
from datetime import datetime, date, timedelta
from typing import Optional

from app.database import get_db, engine
from app.models import (
    Base,
    Customer,
    Account,
    Card,
    Transaction,
    Recommendation,
    Loan,
    User,
)
from app.ai.spending_analyzer import analyze_transactions
from app.ai.financial_health import calculate_financial_health
from app.ai.purchase_decision import purchase_decision
from app.ai.offer_engine import build_offer
from app.ai.recommendation_engine import generate_recommendation
from app.ai.financial_advisor import generate_financial_advice
from app.ai.chat_service import chat_with_ai
from app.services.purchase_service import PurchaseService
from app.services.statement_parser import (
    parse_pdf_statement,
    parse_csv_or_excel,
    parse_image_statement,
    generate_sample_statement,
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Banking Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import JSONResponse
from fastapi.requests import Request

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    response = JSONResponse(
        status_code=500,
        content={"detail": f"Server Error: {str(exc)}"}
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    if ":" in hashed_password:
        salt, h = hashed_password.split(":", 1)
        return hashlib.sha256((salt + plain_password).encode()).hexdigest() == h
    return plain_password == hashed_password or hashed_password == "demo_password_hash_2026"


def ensure_schema_columns(db: Session):
    """Safely migrate any missing columns in existing PostgreSQL or SQLite databases."""
    from sqlalchemy import inspect
    try:
        inspector = inspect(db.bind)
        existing_tables = inspector.get_table_names()

        columns_to_add = [
            ("users", "country", "VARCHAR(50) DEFAULT 'India'"),
            ("users", "preferred_language", "VARCHAR(20) DEFAULT 'en'"),
            ("users", "currency_code", "VARCHAR(10) DEFAULT 'INR'"),
            ("users", "currency_symbol", "VARCHAR(10) DEFAULT '₹'"),
            ("users", "is_active", "VARCHAR(10) DEFAULT 'true'"),
            ("accounts", "currency_symbol", "VARCHAR(10) DEFAULT '$'"),
            ("customers", "country", "VARCHAR(50) DEFAULT 'United States'"),
            ("customers", "currency_code", "VARCHAR(10) DEFAULT 'USD'"),
            ("customers", "currency_symbol", "VARCHAR(10) DEFAULT '$'"),
        ]

        is_sqlite = db.bind.dialect.name == "sqlite"

        for table, col, col_def in columns_to_add:
            if table not in existing_tables:
                continue
            cols = [c["name"] for c in inspector.get_columns(table)]
            if col not in cols:
                try:
                    if is_sqlite:
                        db.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_def};"))
                    else:
                        db.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_def};"))
                    db.commit()
                except Exception as ex:
                    print(f"Schema alter note ({table}.{col}): {ex}")
                    db.rollback()
    except Exception as e:
        print(f"Schema inspection warning: {e}")


try:
    Base.metadata.create_all(bind=engine)
    from app.database import SessionLocal
    with SessionLocal() as _db:
        ensure_schema_columns(_db)
except Exception as _e:
    print(f"Table initialization note: {_e}")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    try:
        from app.database import SessionLocal
        from app.seeder import seed_database_if_empty
        with SessionLocal() as db:
            ensure_schema_columns(db)
            seed_database_if_empty(db)
    except Exception as e:
        print(f"Startup seeding error: {e}")



@app.get("/")
def home():
    return {
        "message": "AI Banking Backend Running"
    }

@app.get("/seed")
@app.post("/seed")
def trigger_seed(force: bool = False, db: Session = Depends(get_db)):
    from app.seeder import seed_database
    return seed_database(db, force=force)


# -------------------------------------------------------------
# AUTHENTICATION ROUTES
# -------------------------------------------------------------

@app.post("/auth/register")
def register_user(body: dict, db: Session = Depends(get_db)):
    try:
        email = body.get("email", "").strip().lower()
        full_name = body.get("full_name", "").strip()
        password = body.get("password", "")
        country = body.get("country", "India")
        preferred_language = body.get("preferred_language", "en")
        currency_code = body.get("currency_code", "INR")
        currency_symbol = body.get("currency_symbol", "₹")

        if not email or not password or not full_name:
            raise HTTPException(status_code=400, detail="Full name, email and password are required")

        from app.seeder import seed_database_if_empty, reset_postgres_sequences
        seed_database_if_empty(db)

        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="An account with this email already exists")

        pwd_hash = hash_password(password)

        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=pwd_hash,
            role="customer",
            country=country,
            preferred_language=preferred_language,
            currency_code=currency_code,
            currency_symbol=currency_symbol,
            is_active="true"
        )
        db.add(new_user)
        db.flush()

        # Determine unique customer_id that is NOT taken
        existing_customer = db.query(Customer).filter(Customer.email == email).first()
        if existing_customer:
            customer = existing_customer
        else:
            max_cust = db.query(func.max(Customer.customer_id)).scalar() or 0
            cand_id = max(max_cust + 1, new_user.id)
            while db.query(Customer).filter(Customer.customer_id == cand_id).first():
                cand_id += 1

            cust_code = f"CUST{cand_id:04d}"
            while db.query(Customer).filter(Customer.customer_code == cust_code).first():
                cand_id += 1
                cust_code = f"CUST{cand_id:04d}"

            customer = Customer(
                customer_id=cand_id,
                customer_code=cust_code,
                full_name=full_name,
                email=email,
                phone="+91-9876543210" if country == "India" else "+1-555-0100",
                salary=0.0,
                customer_since=date.today(),
                kyc_status="VERIFIED",
                country=country,
                currency_code=currency_code,
                currency_symbol=currency_symbol,
            )
            db.add(customer)
            db.flush()

        # Determine unique account_id that is NOT taken
        existing_account = db.query(Account).filter(Account.customer_id == customer.customer_id).first()
        if not existing_account:
            max_acc = db.query(func.max(Account.account_id)).scalar() or 0
            cand_acc_id = max(max_acc + 1, customer.customer_id)
            while db.query(Account).filter(Account.account_id == cand_acc_id).first():
                cand_acc_id += 1

            account = Account(
                account_id=cand_acc_id,
                customer_id=customer.customer_id,
                account_number=f"ACC-{customer.customer_id:04d}8901",
                account_type="Savings",
                balance=0.0,
                savings=0.0,
                monthly_salary=0.0,
                currency_symbol=currency_symbol,
                status="ACTIVE"
            )
            db.add(account)
            db.flush()

        # Determine unique card_id that is NOT taken
        existing_card = db.query(Card).filter(Card.customer_id == customer.customer_id).first()
        if not existing_card:
            max_card = db.query(func.max(Card.card_id)).scalar() or 0
            cand_card_id = max(max_card + 1, customer.customer_id)
            while db.query(Card).filter(Card.card_id == cand_card_id).first():
                cand_card_id += 1

            card = Card(
                card_id=cand_card_id,
                customer_id=customer.customer_id,
                card_number=f"4532-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                expiry_date="12/29",
                cvv=str(random.randint(100, 999)),
                card_type="Visa Platinum",
                status="ACTIVE"
            )
            db.add(card)
            db.flush()

        db.commit()
        reset_postgres_sequences(db)

        return {
            "status": "success",
            "user": {
                "id": new_user.id,
                "customer_id": customer.customer_id,
                "full_name": new_user.full_name,
                "email": new_user.email,
                "country": new_user.country,
                "preferred_language": new_user.preferred_language,
                "currency_code": new_user.currency_code,
                "currency_symbol": new_user.currency_symbol,
                "is_demo": False
            },
            "token": f"token_{new_user.id}_{secrets.token_hex(8)}"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/auth/login")
def login_user(body: dict, db: Session = Depends(get_db)):
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    # Robert Wilson demo login support
    if email in ("robert.wilson@demo.com", "robert.wilson@apexbank.com"):
        user = db.query(User).filter(User.email.in_(["robert.wilson@demo.com", "robert.wilson@apexbank.com"])).first()
        if not user:
            from app.seeder import seed_database
            seed_database(db, force=False)
            user = db.query(User).filter(User.email.in_(["robert.wilson@demo.com", "robert.wilson@apexbank.com"])).first()

        return {
            "status": "success",
            "user": {
                "id": user.id if user else 1,
                "customer_id": 1,
                "full_name": "Robert Wilson",
                "email": "robert.wilson@demo.com",
                "country": "United States",
                "preferred_language": "en",
                "currency_code": "USD",
                "currency_symbol": "$",
                "is_demo": True
            },
            "token": "demo_robert_wilson_token"
        }

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    cust = db.query(Customer).filter(Customer.email == user.email).first()
    cust_id = cust.customer_id if cust else user.id
    tx_count = db.query(func.count(Transaction.transaction_id)).filter(Transaction.customer_id == cust_id).scalar() or 0

    return {
        "status": "success",
        "user": {
            "id": user.id,
            "customer_id": cust_id,
            "full_name": user.full_name,
            "email": user.email,
            "country": user.country or "India",
            "preferred_language": user.preferred_language or "en",
            "currency_code": user.currency_code or "INR",
            "currency_symbol": user.currency_symbol or "₹",
            "is_demo": False,
            "has_transactions": tx_count > 0,
        },
        "token": f"token_{user.id}_{secrets.token_hex(8)}"
    }


@app.post("/auth/forgot-password")
def forgot_password(body: dict, db: Session = Depends(get_db)):
    email = body.get("email", "").strip().lower()
    new_password = body.get("new_password", "")

    if not email or not new_password:
        raise HTTPException(status_code=400, detail="Email and new password are required")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No user found with this email address")

    user.password_hash = hash_password(new_password)
    db.commit()

    return {
        "status": "success",
        "message": "Password updated successfully. You can now log in with your new password."
    }


def perform_user_deletion(db: Session, customer_id: int, user_obj: Optional[User] = None, cust_obj: Optional[Customer] = None):
    """Delete all banking records and user credentials for a non-demo user."""
    cids = {int(customer_id)}
    if user_obj and user_obj.id:
        cids.add(int(user_obj.id))
    if cust_obj and cust_obj.customer_id:
        cids.add(int(cust_obj.customer_id))
    # Never delete customer_id 1 rows from DB so demo can always be re-seeded
    cids.discard(1)

    for cid in cids:
        db.query(Transaction).filter(Transaction.customer_id == cid).delete()
        db.query(Card).filter(Card.customer_id == cid).delete()
        db.query(Loan).filter(Loan.customer_id == cid).delete()
        db.query(Recommendation).filter(Recommendation.customer_id == cid).delete()
        db.query(Account).filter(Account.customer_id == cid).delete()
        db.query(Customer).filter(Customer.customer_id == cid).delete()

    if user_obj and user_obj.id != 1:
        db.query(User).filter(User.id == user_obj.id).delete()
    elif cust_obj and cust_obj.email and cust_obj.customer_id != 1:
        db.query(User).filter(User.email == cust_obj.email).delete()

    db.commit()


@app.post("/auth/delete-account")
def delete_account(body: dict, db: Session = Depends(get_db)):
    customer_id = int(body.get("customer_id") or body.get("id") or 0)
    email = (body.get("email") or "").strip().lower()
    password = (body.get("password") or "").strip()

    if not password:
        raise HTTPException(status_code=400, detail="Password is required to delete the account")

    # Demo Account (Robert Wilson) protection: requires Admin Password 'robert@123'
    if customer_id == 1 or email in ("robert.wilson@demo.com", "robert.wilson@apexbank.com"):
        if password != "robert@123":
            raise HTTPException(
                status_code=403,
                detail="Access Denied: Invalid Admin Password. Demo account cannot be deleted without the admin password."
            )
        return {
            "status": "success",
            "message": "Admin password verified. Demo account deletion completed.",
            "redirect": "/register"
        }

    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    user = db.query(User).filter(User.id == customer_id).first()
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
    if not user and customer and customer.email:
        user = db.query(User).filter(User.email == customer.email).first()

    if not user and not customer:
        raise HTTPException(status_code=404, detail="Account not found")

    if user:
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Incorrect login password. Please enter your valid account password to delete your account."
            )

    perform_user_deletion(db, customer_id, user_obj=user, cust_obj=customer)

    return {
        "status": "success",
        "message": "Your account and all associated data have been permanently deleted.",
        "redirect": "/register"
    }


@app.get("/auth/me")
def get_current_user_info(customer_id: int = 1, db: Session = Depends(get_db)):
    if int(customer_id) == 1:
        return {
            "id": 1,
            "customer_id": 1,
            "full_name": "Robert Wilson",
            "email": "robert.wilson@demo.com",
            "country": "United States",
            "preferred_language": "en",
            "currency_code": "USD",
            "currency_symbol": "$",
            "is_demo": True,
            "has_transactions": True,
        }

    user = db.query(User).filter(User.id == customer_id).first()
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    tx_count = db.query(func.count(Transaction.transaction_id)).filter(Transaction.customer_id == customer_id).scalar() or 0

    if not user:
        if customer:
            return {
                "id": customer_id,
                "customer_id": customer_id,
                "full_name": customer.full_name,
                "email": customer.email,
                "country": getattr(customer, "country", "India"),
                "preferred_language": "en",
                "currency_code": getattr(customer, "currency_code", "INR"),
                "currency_symbol": getattr(customer, "currency_symbol", "₹"),
                "is_demo": False,
                "has_transactions": tx_count > 0,
            }
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "customer_id": customer.customer_id if customer else user.id,
        "full_name": user.full_name,
        "email": user.email,
        "country": user.country or "India",
        "preferred_language": user.preferred_language or "en",
        "currency_code": user.currency_code or "INR",
        "currency_symbol": user.currency_symbol or "₹",
        "is_demo": False,
        "has_transactions": tx_count > 0,
    }


@app.get("/auth/resolve-slug/{slug}")
def resolve_user_by_slug(slug: str, db: Session = Depends(get_db)):
    import re
    clean_slug = re.sub(r"[-_]dashboard$", "", (slug or "").strip(), flags=re.IGNORECASE).lower()
    clean_slug = re.sub(r"[^a-z0-9_-]", "", clean_slug)

    if clean_slug in ("robert", "demo", "robertwilson"):
        from app.seeder import ensure_robert_demo_data
        ensure_robert_demo_data(db, force_restore=False)
        return {
            "id": 1,
            "customer_id": 1,
            "full_name": "Robert Wilson",
            "email": "robert.wilson@demo.com",
            "country": "United States",
            "preferred_language": "en",
            "currency_code": "USD",
            "currency_symbol": "$",
            "is_demo": True,
            "has_transactions": True,
        }

    def extract_slug(name_str: str, email_str: str = "") -> str:
        raw = (name_str or (email_str.split("@")[0] if email_str else "") or "user").strip()
        first = raw.split()[0] if raw.split() else "user"
        return re.sub(r"[^a-z0-9_-]", "", first.lower()) or "user"

    candidates = []
    all_users = db.query(User).all()
    for u in all_users:
        if u.id == 1:
            continue
        u_slug = extract_slug(u.full_name, u.email)
        if u_slug == clean_slug:
            cust = db.query(Customer).filter(Customer.email == u.email).first() or db.query(Customer).filter(Customer.customer_id == u.id).first()
            cid = cust.customer_id if cust else u.id
            tx_cnt = db.query(func.count(Transaction.transaction_id)).filter(Transaction.customer_id == cid).scalar() or 0
            candidates.append((tx_cnt > 0, tx_cnt, cid, {
                "id": u.id,
                "customer_id": cid,
                "full_name": u.full_name,
                "email": u.email,
                "country": u.country or "India",
                "preferred_language": u.preferred_language or "en",
                "currency_code": u.currency_code or "INR",
                "currency_symbol": u.currency_symbol or "₹",
                "is_demo": False,
                "has_transactions": tx_cnt > 0,
            }))

    all_customers = db.query(Customer).all()
    seen_cids = {c[2] for c in candidates}
    for c in all_customers:
        if c.customer_id == 1 or c.customer_id in seen_cids:
            continue
        c_slug = extract_slug(c.full_name, c.email)
        if c_slug == clean_slug:
            tx_cnt = db.query(func.count(Transaction.transaction_id)).filter(Transaction.customer_id == c.customer_id).scalar() or 0
            candidates.append((tx_cnt > 0, tx_cnt, c.customer_id, {
                "id": c.customer_id,
                "customer_id": c.customer_id,
                "full_name": c.full_name,
                "email": c.email,
                "country": getattr(c, "country", "India") or "India",
                "preferred_language": "en",
                "currency_code": getattr(c, "currency_code", "INR") or "INR",
                "currency_symbol": getattr(c, "currency_symbol", "₹") or "₹",
                "is_demo": False,
                "has_transactions": tx_cnt > 0,
            }))

    if candidates:
        candidates.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
        return candidates[0][3]

    raise HTTPException(status_code=404, detail=f"No user found for slug '{clean_slug}'")


# -------------------------------------------------------------
# STATEMENT UPLOAD & DATA MANAGEMENT ROUTES
# -------------------------------------------------------------

@app.post("/statements/upload")
async def upload_statement(
    file: UploadFile = File(...),
    customer_id: int = Form(...),
    country: str = Form("India"),
    currency: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    filename = file.filename.lower() if file.filename else "statement.pdf"

    if filename.endswith(".pdf"):
        data = parse_pdf_statement(contents, country=country)
    elif filename.endswith((".xlsx", ".xls", ".csv")):
        data = parse_csv_or_excel(contents, filename, country=country)
    elif filename.endswith((".png", ".jpg", ".jpeg", ".webp")):
        mime_type = file.content_type or "image/png"
        data = parse_image_statement(contents, mime_type, country=country)
    else:
        data = generate_sample_statement(currency=currency or "INR", country=country)

    # 1. Update or create Account
    account = db.query(Account).filter(Account.customer_id == customer_id).first()
    if not account:
        max_acc = db.query(func.max(Account.account_id)).scalar() or 0
        cand_acc_id = max(max_acc + 1, customer_id)
        while db.query(Account).filter(Account.account_id == cand_acc_id).first():
            cand_acc_id += 1

        account = Account(
            account_id=cand_acc_id,
            customer_id=customer_id,
            account_number=f"ACC-{customer_id:04d}8901",
            account_type="Savings",
            balance=data["total_balance"],
            savings=data["savings"],
            monthly_salary=data["monthly_income"],
            currency_symbol=data["currency_symbol"],
            status="ACTIVE"
        )
        db.add(account)
    else:
        account.balance = data["total_balance"]
        account.savings = data["savings"]
        account.monthly_salary = data["monthly_income"]
        account.currency_symbol = data["currency_symbol"]

    # 2. Update Customer
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if customer:
        customer.salary = data["monthly_income"]
        customer.currency_code = data["currency_code"]
        customer.currency_symbol = data["currency_symbol"]
        customer.country = country

    # 3. Update User
    user = db.query(User).filter(User.id == customer_id).first()
    if user:
        user.currency_code = data["currency_code"]
        user.currency_symbol = data["currency_symbol"]
        user.country = country

    # 4. Ensure Card exists
    card = db.query(Card).filter(Card.customer_id == customer_id).first()
    if not card:
        max_card = db.query(func.max(Card.card_id)).scalar() or 0
        cand_card_id = max(max_card + 1, customer_id)
        while db.query(Card).filter(Card.card_id == cand_card_id).first():
            cand_card_id += 1
        card = Card(
            card_id=cand_card_id,
            customer_id=customer_id,
            card_number=f"4532-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            expiry_date="12/29",
            cvv=str(random.randint(100, 999)),
            card_type="Visa Platinum",
            status="ACTIVE"
        )
        db.add(card)

    # 5. Remove previous statement transactions for this customer
    db.query(Transaction).filter(Transaction.customer_id == customer_id).delete()

    # 6. Insert newly extracted transactions
    for t in data["transactions"]:
        d_val = t.get("transaction_date")
        if isinstance(d_val, str):
            try:
                d_val = datetime.strptime(d_val, "%Y-%m-%d").date()
            except Exception:
                d_val = date.today()
        elif not isinstance(d_val, date):
            d_val = date.today()

        new_txn = Transaction(
            customer_id=customer_id,
            merchant_name=t["merchant_name"],
            category=t["category"],
            amount=t["amount"],
            transaction_type=t["transaction_type"],
            payment_method=t.get("payment_method", "Card"),
            transaction_date=d_val,
            ai_score=t.get("ai_score", "1")
        )
        db.add(new_txn)

    db.commit()
    from app.seeder import reset_postgres_sequences
    reset_postgres_sequences(db)

    return {
        "status": "success",
        "message": f"Successfully parsed and loaded {len(data['transactions'])} transactions from statement.",
        "currency_code": data["currency_code"],
        "currency_symbol": data["currency_symbol"],
        "total_balance": data["total_balance"],
        "monthly_income": data["monthly_income"],
        "monthly_expenses": data["monthly_expenses"],
        "savings": data["savings"],
        "transactions_count": len(data["transactions"]),
    }


@app.post("/statements/sample")
def load_sample(
    body: Optional[dict] = Body(default=None),
    customer_id: Optional[int] = None,
    currency: Optional[str] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    b = body or {}
    customer_id = b.get("customer_id") or customer_id or 1
    currency = b.get("currency") or currency or "INR"
    country = b.get("country") or country or "India"

    data = generate_sample_statement(currency=currency, country=country)

    account = db.query(Account).filter(Account.customer_id == customer_id).first()
    if not account:
        max_acc = db.query(func.max(Account.account_id)).scalar() or 0
        cand_acc_id = max(max_acc + 1, customer_id)
        while db.query(Account).filter(Account.account_id == cand_acc_id).first():
            cand_acc_id += 1

        account = Account(
            account_id=cand_acc_id,
            customer_id=customer_id,
            account_number=f"ACC-{customer_id:04d}8901",
            account_type="Savings",
            balance=data["total_balance"],
            savings=data["savings"],
            monthly_salary=data["monthly_income"],
            currency_symbol=data["currency_symbol"],
            status="ACTIVE"
        )
        db.add(account)
    else:
        account.balance = data["total_balance"]
        account.savings = data["savings"]
        account.monthly_salary = data["monthly_income"]
        account.currency_symbol = data["currency_symbol"]

    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if customer:
        customer.salary = data["monthly_income"]
        customer.currency_code = data["currency_code"]
        customer.currency_symbol = data["currency_symbol"]
        customer.country = country

    user = db.query(User).filter(User.id == customer_id).first()
    if user:
        user.currency_code = data["currency_code"]
        user.currency_symbol = data["currency_symbol"]
        user.country = country

    card = db.query(Card).filter(Card.customer_id == customer_id).first()
    if not card:
        max_card = db.query(func.max(Card.card_id)).scalar() or 0
        cand_card_id = max(max_card + 1, customer_id)
        while db.query(Card).filter(Card.card_id == cand_card_id).first():
            cand_card_id += 1
        card = Card(
            card_id=cand_card_id,
            customer_id=customer_id,
            card_number=f"4532-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            expiry_date="12/29",
            cvv=str(random.randint(100, 999)),
            card_type="Visa Platinum",
            status="ACTIVE"
        )
        db.add(card)

    db.query(Transaction).filter(Transaction.customer_id == customer_id).delete()

    for t in data["transactions"]:
        d_val = t.get("transaction_date")
        if isinstance(d_val, str):
            try:
                d_val = datetime.strptime(d_val, "%Y-%m-%d").date()
            except Exception:
                d_val = date.today()

        new_txn = Transaction(
            customer_id=customer_id,
            merchant_name=t["merchant_name"],
            category=t["category"],
            amount=t["amount"],
            transaction_type=t["transaction_type"],
            payment_method=t.get("payment_method", "Card"),
            transaction_date=d_val,
            ai_score=t.get("ai_score", "1")
        )
        db.add(new_txn)

    db.commit()
    from app.seeder import reset_postgres_sequences
    reset_postgres_sequences(db)

    return {
        "status": "success",
        "message": f"Sample statement ({data['currency_code']}) loaded successfully.",
        "currency_code": data["currency_code"],
        "currency_symbol": data["currency_symbol"],
        "total_balance": data["total_balance"],
        "monthly_income": data["monthly_income"],
        "monthly_expenses": data["monthly_expenses"],
        "savings": data["savings"],
        "transactions_count": len(data["transactions"]),
    }


@app.post("/statements/clear")
def clear_statement_data(
    body: Optional[dict] = Body(default=None),
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    b = body or {}
    cid = b.get("customer_id") or customer_id
    if not cid:
        raise HTTPException(status_code=400, detail="customer_id is required")
    customer_id = cid

    # Delete transactions for this customer
    db.query(Transaction).filter(Transaction.customer_id == customer_id).delete()

    # Reset account balance and savings
    account = db.query(Account).filter(Account.customer_id == customer_id).first()
    if account:
        account.balance = 0.0
        account.savings = 0.0
        account.monthly_salary = 0.0

    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if customer:
        customer.salary = 0.0

    db.commit()

    return {
        "status": "success",
        "message": "User statement data and transactions cleared successfully."
    }


# -------------------------------------------------------------
# USER-SCOPED BANKING ROUTES
# -------------------------------------------------------------

@app.get("/customers")
def customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()


@app.get("/accounts")
def accounts(customer_id: Optional[int] = None, db: Session = Depends(get_db)):
    if customer_id:
        return db.query(Account).filter(Account.customer_id == customer_id).all()
    return db.query(Account).all()


@app.get("/cards")
def cards(customer_id: Optional[int] = None, db: Session = Depends(get_db)):
    if customer_id:
        return db.query(Card).filter(Card.customer_id == customer_id).all()
    return db.query(Card).all()


@app.get("/transactions")
def transactions(customer_id: int = 1, cleared: bool = False, db: Session = Depends(get_db)):
    if customer_id == 1 and not cleared:
        from app.seeder import ensure_robert_demo_data
        ensure_robert_demo_data(db, force_restore=False)
    return db.query(Transaction).filter(Transaction.customer_id == customer_id).order_by(Transaction.transaction_date.desc()).all()


@app.get("/recommendations")
def recommendations(customer_id: Optional[int] = None, db: Session = Depends(get_db)):
    if customer_id:
        return db.query(Recommendation).filter(Recommendation.customer_id == customer_id).all()
    return db.query(Recommendation).all()


@app.get("/loans")
def loans(customer_id: Optional[int] = None, db: Session = Depends(get_db)):
    if customer_id:
        return db.query(Loan).filter(Loan.customer_id == customer_id).all()
    return db.query(Loan).all()


@app.get("/ai/analyze/{customer_id}")
def analyze(customer_id: int,
            cleared: bool = False,
            db: Session = Depends(get_db)):
    if customer_id == 1 and not cleared:
        from app.seeder import ensure_robert_demo_data
        ensure_robert_demo_data(db, force_restore=False)

    transactions = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .all()
    )

    return analyze_transactions(transactions)

@app.get("/ai/financial-health/{customer_id}")
def financial_health(customer_id: int,
                     cleared: bool = False,
                     db: Session = Depends(get_db)):
    if customer_id == 1 and not cleared:
        from app.seeder import ensure_robert_demo_data
        ensure_robert_demo_data(db, force_restore=False)

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
        from app.seeder import seed_database
        seed_database(db, force=False)
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        account = db.query(Account).filter(Account.customer_id == customer_id).first()
        transactions = db.query(Transaction).filter(Transaction.customer_id == customer_id).all()

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


def _is_cancel_delete(q: str) -> bool:
    q_low = (q or "").lower().strip()
    return q_low in (
        "cancel", "stop", "abort", "no", "nahi", "nhi", "mat karo",
        "keep", "keep my account", "don't delete", "dont delete", "rehne do"
    )


def _is_delete_account_intent(q: str) -> bool:
    q_low = (q or "").lower()
    has_action = any(w in q_low for w in [
        "delete", "remove", "close", "deactivate", "band", "hata", "khatam",
        "डिलीट", "हटा", "बंद", "समाप्त"
    ])
    has_target = any(w in q_low for w in [
        "account", "profile", "khata", "खाता", "अकाउंट", "प्रोफाइल"
    ])
    return (has_action and has_target) or q_low.strip() in (
        "delete my account", "delete account", "account delete", "mera account delete karo"
    )


def _is_confirm_delete_intent(q: str) -> bool:
    q_low = (q or "").lower().strip()
    if _is_cancel_delete(q_low):
        return False
    if _is_delete_account_intent(q_low):
        return True
    return any(w in q_low for w in [
        "yes", "haan", "ha", "sure", "confirm", "proceed", "still", "delete",
        "kar do", "kardo", "karna", "चाहता", "हां", "हाँ", "कर दो", "ok", "yep", "yeah", "please"
    ])


@app.post("/ai/chat")
def ai_chat(
    body: dict,
    db: Session = Depends(get_db)
):
    customer_id = body.get("customer_id", 1)
    language = body.get("language", "en")
    cleared = bool(body.get("cleared", False))
    delete_stage = (body.get("delete_stage") or "none").strip().lower()

    if int(customer_id) == 1 and not cleared:
        from app.seeder import ensure_robert_demo_data
        ensure_robert_demo_data(db, force_restore=False)

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

    user = db.query(User).filter(User.id == customer_id).first()
    if not user and customer and customer.email:
        user = db.query(User).filter(User.email == customer.email).first()

    if int(customer_id) == 1:
        currency_symbol = "$"
    else:
        currency_symbol = (
            getattr(account, "currency_symbol", None) or
            getattr(customer, "currency_symbol", None) or
            (user.currency_symbol if user else None) or
            "₹"
        )
    if not language and user and user.preferred_language:
        language = user.preferred_language

    if not customer or not account:
        if customer_id == 1:
            from app.seeder import seed_database
            seed_database(db, force=False)
            customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
            account = db.query(Account).filter(Account.customer_id == customer_id).first()
        elif user:
            customer = Customer(
                customer_id=user.id,
                customer_code=f"CUST{user.id:04d}",
                full_name=user.full_name,
                email=user.email,
                salary=0.0,
                kyc_status="VERIFIED",
                currency_symbol=currency_symbol,
            )
            db.add(customer)
            account = Account(
                account_id=user.id,
                customer_id=user.id,
                account_number=f"ACC-{user.id:04d}8901",
                account_type="Savings",
                balance=0.0,
                savings=0.0,
                monthly_salary=0.0,
                currency_symbol=currency_symbol,
                status="ACTIVE",
            )
            db.add(account)
            db.commit()

    question = (body.get("question") or body.get("message") or "").strip()
    cust_name = customer.full_name if customer else (user.full_name if user else "Customer")
    curr_bal = float(account.balance) if account else 0.0

    # ---------------------------------------------------------
    # 3-STEP CONVERSATIONAL ACCOUNT DELETION FLOW IN AI ADVISOR
    # ---------------------------------------------------------
    # Step 3: Awaiting password verification
    if delete_stage == "awaiting_password":
        if _is_cancel_delete(question):
            msg = (
                f"### ✅ Account Deletion Cancelled\n\n"
                f"Great choice, **{cust_name}**! Your account and financial data remain completely safe and active. "
                f"Ask me anything about your spending, savings, or loan options!"
            )
            return {
                "customer": cust_name,
                "question": question,
                "answer": msg,
                "reply": msg,
                "delete_step": "none",
                "account_deleted": False,
                "account": {"balance": curr_bal, "status": "ACTIVE", "currency_symbol": currency_symbol},
                "offer": None,
            }

        tokens = [question.strip()] + question.strip().split()
        if int(customer_id) == 1:
            # Demo account requires Admin Password: robert@123
            if any(tok == "robert@123" for tok in tokens):
                msg = (
                    "### ✅ Admin Password Verified — Deleting Account...\n\n"
                    "- 🛡️ **Admin Authorization:** Verified (`Robert Wilson` Demo Account)\n"
                    "- 🗑️ **Deletion Process:** Clearing active session & account state...\n"
                    "- 🔄 **Completed:** Redirecting you to the **Create Account** page..."
                )
                return {
                    "customer": cust_name,
                    "question": "••••••••",
                    "answer": msg,
                    "reply": msg,
                    "delete_step": "deleted",
                    "account_deleted": True,
                    "account": {"balance": 0.0, "status": "DELETED", "currency_symbol": currency_symbol},
                    "offer": None,
                }
            else:
                msg = (
                    "### ❌ Access Denied — Invalid Admin Password\n\n"
                    "**Robert Wilson's Demo Account** is protected and cannot be deleted without the valid **Admin Password**.\n\n"
                    "🛡️ Please enter the correct **Admin Password** in your next message to proceed, or type `cancel` to abort."
                )
                return {
                    "customer": cust_name,
                    "question": "••••••••",
                    "answer": msg,
                    "reply": msg,
                    "delete_step": "awaiting_password",
                    "account_deleted": False,
                    "account": {"balance": curr_bal, "status": "ACTIVE", "currency_symbol": currency_symbol},
                    "offer": None,
                }
        else:
            # Regular user account: verify user's login password
            is_valid_pwd = bool(user and any(verify_password(tok, user.password_hash) for tok in tokens))
            if is_valid_pwd:
                perform_user_deletion(db, int(customer_id), user_obj=user, cust_obj=customer)
                msg = (
                    f"### ✅ Password Verified — Account Deleted Successfully\n\n"
                    f"- 🔐 **Identity Verified:** Password matched for **{cust_name}**\n"
                    f"- 🗑️ **Deletion Process:** Removed all uploaded bank statements, transactions, and account credentials\n"
                    f"- 🔄 **Completed:** Redirecting you to the **Create Account** page..."
                )
                return {
                    "customer": cust_name,
                    "question": "••••••••",
                    "answer": msg,
                    "reply": msg,
                    "delete_step": "deleted",
                    "account_deleted": True,
                    "account": {"balance": 0.0, "status": "DELETED", "currency_symbol": currency_symbol},
                    "offer": None,
                }
            else:
                msg = (
                    f"### ❌ Incorrect Account Password\n\n"
                    f"The password you entered does not match the login password for **{cust_name}**.\n\n"
                    f"🔑 Please enter your valid **login password** in your next response to delete your account, or type `cancel` to abort."
                )
                return {
                    "customer": cust_name,
                    "question": "••••••••",
                    "answer": msg,
                    "reply": msg,
                    "delete_step": "awaiting_password",
                    "account_deleted": False,
                    "account": {"balance": curr_bal, "status": "ACTIVE", "currency_symbol": currency_symbol},
                    "offer": None,
                }

    # Step 2: User was already convinced once and still insists on deleting
    if delete_stage == "convinced_once":
        if _is_cancel_delete(question):
            msg = (
                f"### 🎉 Glad You Decided to Stay, {cust_name}!\n\n"
                f"Your account is completely safe and active. How can I help you optimize your finances today?"
            )
            return {
                "customer": cust_name,
                "question": question,
                "answer": msg,
                "reply": msg,
                "delete_step": "none",
                "account_deleted": False,
                "account": {"balance": curr_bal, "status": "ACTIVE", "currency_symbol": currency_symbol},
                "offer": None,
            }
        if _is_confirm_delete_intent(question):
            if int(customer_id) == 1:
                msg = (
                    "### 🛡️ Demo Account Protection — Admin Password Required\n\n"
                    "Since **Robert Wilson** is the protected **Demo Account**, standard users are not permitted to delete it.\n\n"
                    "🔐 **Please enter the Admin Password in your next response** to start the account deletion process (or type `cancel` to abort)."
                )
            else:
                msg = (
                    f"### 🔐 Password Required to Delete Account\n\n"
                    f"I respect your decision to delete your account (**{cust_name}**).\n\n"
                    f"🔑 **Please enter your profile login password in your next response** so I can start the account deletion process (or type `cancel` to abort)."
                )
            return {
                "customer": cust_name,
                "question": question,
                "answer": msg,
                "reply": msg,
                "delete_step": "awaiting_password",
                "account_deleted": False,
                "account": {"balance": curr_bal, "status": "ACTIVE", "currency_symbol": currency_symbol},
                "offer": None,
            }
        # If they asked a normal financial question instead, reset delete_stage and answer normally
        delete_stage = "none"

    # Step 1: First time user asks AI Advisor to delete their account -> Convince them once!
    if delete_stage == "none" and _is_delete_account_intent(question):
        msg = (
            f"### ⚠️ Wait, {cust_name}! Please Reconsider Deleting Your Account\n\n"
            f"We'd hate to see you go! With your active AI Banking profile, you currently have access to:\n"
            f"- 📊 **Smart Statement Analytics** (Current Balance: `{currency_symbol}{curr_bal:,.2f}`)\n"
            f"- ❤️ **AI Financial Health Monitoring & Category Insights**\n"
            f"- 💳 **Instant Pre-Approved Loan & EMI Discount Offers**\n\n"
            f"💡 *Note: If you only want to remove your uploaded statement transactions, you can click **Clear Data** on the dashboard anytime while keeping your account!*\n\n"
            f"👉 **Do you still want to permanently delete your account?** If you are sure, reply **\"Yes, delete my account\"** (or type `cancel` to keep your account)."
        )
        return {
            "customer": cust_name,
            "question": question,
            "answer": msg,
            "reply": msg,
            "delete_step": "convinced_once",
            "account_deleted": False,
            "account": {"balance": curr_bal, "status": "ACTIVE", "currency_symbol": currency_symbol},
            "offer": None,
        }

    if not customer or not account:
        return {
            "customer": cust_name,
            "question": question,
            "answer": "Please upload a bank statement to enable AI financial analysis.",
            "delete_step": "none",
            "account_deleted": False,
            "account": {
                "balance": 0.0,
                "status": "ACTIVE",
                "currency_symbol": currency_symbol,
            },
            "offer": None,
        }

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

    offer = build_offer(
        customer,
        account,
        spending,
        health,
        question,
        currency_symbol=currency_symbol,
    )

    answer = chat_with_ai(
        customer,
        account,
        spending,
        health,
        question,
        offer,
        currency_symbol=currency_symbol,
        language=language,
    )

    return {
        "customer": customer.full_name,
        "question": question,
        "answer": answer,
        "reply": answer,
        "delete_step": "none",
        "account_deleted": False,
        "account": {
            "balance": float(account.balance),
            "status": account.status,
            "currency_symbol": currency_symbol,
        },
        "offer": offer,
    }


@app.get("/dashboard")
def get_dashboard(customer_id: int = 1, cleared: bool = False, db: Session = Depends(get_db)):
    if customer_id == 1 and not cleared:
        from app.seeder import ensure_robert_demo_data
        ensure_robert_demo_data(db, force_restore=False)

    account = db.query(Account).filter(Account.customer_id == customer_id).first()
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    user = db.query(User).filter(User.id == customer_id).first()

    if not account or not customer:
        if customer_id == 1:
            from app.seeder import seed_database
            seed_database(db, force=False)
            account = db.query(Account).filter(Account.customer_id == 1).first()
            customer = db.query(Customer).filter(Customer.customer_id == 1).first()
        elif user:
            customer = Customer(
                customer_id=user.id,
                customer_code=f"CUST{user.id:04d}",
                full_name=user.full_name,
                email=user.email,
                salary=0.0,
                kyc_status="VERIFIED",
                currency_symbol=user.currency_symbol or "₹",
            )
            db.add(customer)
            account = Account(
                account_id=user.id,
                customer_id=user.id,
                account_number=f"ACC-{user.id:04d}8901",
                account_type="Savings",
                balance=0.0,
                savings=0.0,
                monthly_salary=0.0,
                currency_symbol=user.currency_symbol or "₹",
                status="ACTIVE",
            )
            db.add(account)
            db.commit()

    if not account or not customer:
        return {
            "customer_name": "Customer",
            "currency_symbol": "₹",
            "balance": 0.0,
            "income": 0.0,
            "expenses": 0.0,
            "savings": 0.0,
            "health_score": 0,
            "health_status": "No Statement Uploaded",
            "insights": {
                "balance": "Upload bank statement to view liquidity analysis",
                "income": "Upload bank statement to view cash flow",
                "expenses": "Upload bank statement to view spending",
                "savings": "Upload bank statement to track savings habit"
            }
        }

    transactions = db.query(Transaction).filter(Transaction.customer_id == customer_id).all()
    total_debits = sum(float(t.amount) for t in transactions if t.transaction_type == "Debit")

    num_months = 1
    dates_found = [t.transaction_date for t in transactions if t.transaction_date]
    if dates_found:
        span_days = max(1, (max(dates_found) - min(dates_found)).days)
        num_months = max(1, round(span_days / 30.0))

    monthly_expenses = round(total_debits / num_months, 2) if total_debits > 0 else 0.0

    health = calculate_financial_health(
        customer,
        account,
        transactions
    )

    if customer_id == 1:
        currency_sym = "$"
    else:
        currency_sym = getattr(customer, "currency_symbol", None) or getattr(account, "currency_symbol", None) or (user.currency_symbol if user else "₹") or "₹"

    return {
        "customer_name": customer.full_name,
        "currency_symbol": currency_sym,
        "balance": float(account.balance),
        "income": float(account.monthly_salary),
        "expenses": float(monthly_expenses),
        "savings": float(account.savings),

        "health_score": health["financial_health_score"],
        "health_status": health["status"],

        "insights": {
            "balance": "↑ Strong liquidity position" if float(account.balance) > 0 else "Upload statement to check balance",
            "income": "Stable monthly cash flow" if float(account.monthly_salary) > 0 else "No monthly income recorded",
            "expenses": "Spending tracked from statement" if float(monthly_expenses) > 0 else "No expenses recorded",
            "savings": "Healthy emergency fund buffer" if float(account.savings) > 0 else "Start saving to build a buffer"
        }
    }


@app.get("/spending-chart")
def spending_chart(customer_id: int = 1, cleared: bool = False, db: Session = Depends(get_db)):
    if customer_id == 1 and not cleared:
        from app.seeder import ensure_robert_demo_data
        ensure_robert_demo_data(db, force_restore=False)

    transactions = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id, Transaction.transaction_type == "Debit")
        .all()
    )

    months = {
        "Jan": 0.0,
        "Feb": 0.0,
        "Mar": 0.0,
        "Apr": 0.0,
        "May": 0.0,
        "Jun": 0.0,
        "Jul": 0.0,
        "Aug": 0.0,
        "Sep": 0.0,
        "Oct": 0.0,
        "Nov": 0.0,
        "Dec": 0.0,
    }

    for t in transactions:
        month = t.transaction_date.strftime("%b")
        if month in months:
            months[month] += float(t.amount)

    return [
        {"month": k, "expense": round(v, 2)}
        for k, v in months.items()
    ]



@app.post("/demo/reset/{customer_id}")
def reset_demo_account(customer_id: int, db: Session = Depends(get_db)):
    if int(customer_id) == 1:
        from app.seeder import ensure_robert_demo_data
        ensure_robert_demo_data(db, force_restore=False)
    account = db.query(Account).filter(
        Account.customer_id == customer_id
    ).first()
    if not account:
        from app.seeder import seed_database
        seed_database(db, force=False)
    service = PurchaseService(db)
    return service.reset_demo_account(customer_id)


@app.post("/offers/accept")
def accept_offer(body: dict, db: Session = Depends(get_db)):
    customer_id = body["customer_id"]
    offer = body["offer"]

    account = db.query(Account).filter(
        Account.customer_id == customer_id
    ).first()

    service = PurchaseService(db)

    return service.execute_purchase(
        customer_id=customer_id,
        offer=offer,
        account=account,
    )
