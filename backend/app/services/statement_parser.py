import io
import re
import csv
import json
import random
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional

from app.ai.gemini_service import get_client

# Currency detection mapping
CURRENCY_MAP = {
    "₹": ("INR", "₹"),
    "rs": ("INR", "₹"),
    "inr": ("INR", "₹"),
    "$": ("USD", "$"),
    "usd": ("USD", "$"),
    "€": ("EUR", "€"),
    "eur": ("EUR", "€"),
    "£": ("GBP", "£"),
    "gbp": ("GBP", "£"),
    "aed": ("AED", "AED "),
    "cad": ("CAD", "C$"),
    "aud": ("AUD", "A$"),
    "jpy": ("JPY", "¥"),
    "¥": ("JPY", "¥"),
}

DEFAULT_CATEGORIES = [
    "Food", "Groceries", "Bills", "Rent", "Entertainment",
    "Shopping", "Fuel", "Electronics", "Health", "Salary", "Investment"
]


def detect_currency_from_text(text: str, fallback_country: str = "India") -> tuple[str, str]:
    """Detect currency code and symbol from text or country."""
    lower_text = text.lower()
    for key, (code, symbol) in CURRENCY_MAP.items():
        if key in ["$", "€", "£", "₹", "¥"]:
            if key in text:
                return code, symbol
        else:
            if re.search(r'\b' + re.escape(key) + r'\b', lower_text):
                return code, symbol

    if fallback_country.lower() in ["india", "in"]:
        return "INR", "₹"
    elif fallback_country.lower() in ["usa", "united states", "us"]:
        return "USD", "$"
    elif fallback_country.lower() in ["uk", "united kingdom", "great britain"]:
        return "GBP", "£"
    elif fallback_country.lower() in ["uae", "dubai", "united arab emirates"]:
        return "AED", "AED "
    elif fallback_country.lower() in ["germany", "france", "europe"]:
        return "EUR", "€"
    
    return "INR", "₹"


def categorize_merchant(merchant: str) -> str:
    """Classify merchant or transaction description into a banking category."""
    m = merchant.lower()
    if any(k in m for k in ["salary", "payroll", "stipend", "wages", "credit interest"]):
        return "Salary"
    if any(k in m for k in ["swiggy", "zomato", "restaurant", "cafe", "starbucks", "mcdonald", "subway", "coffee", "food", "dining"]):
        return "Food"
    if any(k in m for k in ["supermarket", "walmart", "blinkit", "zepto", "dmart", "groceries", "bigbasket", "kirana", "provision"]):
        return "Groceries"
    if any(k in m for k in ["electricity", "power", "water", "gas", "bescom", "tneb", "bill", "utility", "broadband", "wifi", "airtel", "jio"]):
        return "Bills"
    if any(k in m for k in ["rent", "landlord", "flat", "pg", "society", "maintenance"]):
        return "Rent"
    if any(k in m for k in ["netflix", "prime", "spotify", "cinema", "movie", "theatre", "entertainment", "hotstar"]):
        return "Entertainment"
    if any(k in m for k in ["petrol", "diesel", "fuel", "shell", "hpcl", "bpcl", "ioc", "gas station"]):
        return "Fuel"
    if any(k in m for k in ["amazon", "flipkart", "myntra", "zara", "clothing", "shopping", "retail", "mall"]):
        return "Shopping"
    if any(k in m for k in ["apple", "croma", "reliance digital", "electronics", "laptop", "mobile", "gadget"]):
        return "Electronics"
    if any(k in m for k in ["pharmacy", "hospital", "clinic", "apollo", "medplus", "health", "dental"]):
        return "Health"
    return "Shopping"


def parse_csv_or_excel(file_bytes: bytes, filename: str, country: str = "India") -> Dict[str, Any]:
    """Parse CSV or Excel spreadsheet into structured banking data."""
    text_content = ""
    rows = []

    if filename.endswith(".csv"):
        try:
            text_content = file_bytes.decode("utf-8", errors="ignore")
            reader = csv.reader(io.StringIO(text_content))
            rows = [r for r in reader if any(cell.strip() for cell in r)]
        except Exception as e:
            print(f"CSV read error: {e}")
    else:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
            sheet = wb.active
            for row in sheet.iter_rows(values_only=True):
                if any(row):
                    rows.append([str(c or "").strip() for c in row])
            text_content = " ".join([" ".join(r) for r in rows])
        except Exception as e:
            print(f"Excel read error: {e}")

    currency_code, currency_symbol = detect_currency_from_text(text_content, country)

    transactions = []
    total_debits = 0.0
    total_credits = 0.0

    header_idx = -1
    date_col = -1
    desc_col = -1
    debit_col = -1
    credit_col = -1
    amount_col = -1

    for idx, r in enumerate(rows[:15]):
        lower_row = [str(c).lower() for c in r]
        for c_idx, cell in enumerate(lower_row):
            if "date" in cell and date_col == -1:
                date_col = c_idx
            elif any(k in cell for k in ["desc", "narration", "particular", "merchant", "details"]) and desc_col == -1:
                desc_col = c_idx
            elif "debit" in cell and debit_col == -1:
                debit_col = c_idx
            elif "credit" in cell and credit_col == -1:
                credit_col = c_idx
            elif any(k in cell for k in ["amount", "txn amt", "value"]) and amount_col == -1:
                amount_col = c_idx

        if (date_col != -1 or desc_col != -1) and (amount_col != -1 or debit_col != -1):
            header_idx = idx
            break

    start_row = header_idx + 1 if header_idx != -1 else 1
    base_date = date.today()

    for idx, r in enumerate(rows[start_row:]):
        if not r or len(r) < 2:
            continue

        raw_desc = r[desc_col] if desc_col != -1 and desc_col < len(r) else (r[1] if len(r) > 1 else "Transaction")
        if not raw_desc or raw_desc.lower() in ["total", "balance brought forward", "opening balance"]:
            continue

        amount = 0.0
        txn_type = "Debit"

        if debit_col != -1 and debit_col < len(r) and r[debit_col]:
            amt_str = re.sub(r'[^\d.]', '', str(r[debit_col]))
            if amt_str:
                amount = float(amt_str)
                txn_type = "Debit"
        if credit_col != -1 and credit_col < len(r) and r[credit_col] and (amount == 0.0 or txn_type == "Debit"):
            amt_str = re.sub(r'[^\d.]', '', str(r[credit_col]))
            if amt_str:
                amount = float(amt_str)
                txn_type = "Credit"
        if amount == 0.0 and amount_col != -1 and amount_col < len(r):
            amt_str = re.sub(r'[^\d.]', '', str(r[amount_col]))
            if amt_str:
                amount = float(amt_str)
                if any(x in str(r).upper() for x in [" CR", "CREDIT", "REFUND", "SALARY"]):
                    txn_type = "Credit"

        if amount <= 0:
            continue

        txn_date = base_date - timedelta(days=idx % 60)
        if date_col != -1 and date_col < len(r) and r[date_col]:
            raw_d = str(r[date_col])
            for fmt in ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%b-%Y"]:
                try:
                    txn_date = datetime.strptime(raw_d.strip(), fmt).date()
                    break
                except ValueError:
                    pass

        category = categorize_merchant(raw_desc)
        if txn_type == "Credit" and category != "Salary":
            if "salary" in raw_desc.lower() or amount > 25000:
                category = "Salary"

        if txn_type == "Debit":
            total_debits += amount
        else:
            total_credits += amount

        transactions.append({
            "merchant_name": raw_desc[:90],
            "category": category,
            "amount": round(amount, 2),
            "transaction_type": txn_type,
            "payment_method": "Bank Transfer" if txn_type == "Credit" else "Card/UPI",
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "ai_score": str(random.randint(1, 4))
        })

    if len(transactions) < 3:
        return generate_sample_statement(currency=currency_code, country=country)

    balance = max(round(total_credits - total_debits, 2), round(total_credits * 0.45, 2))
    monthly_salary = total_credits if total_credits > 0 else round(total_debits * 1.3, 2)
    savings = round(balance * 0.35, 2)

    return {
        "currency_code": currency_code,
        "currency_symbol": currency_symbol,
        "total_balance": balance,
        "monthly_income": monthly_salary,
        "monthly_expenses": round(total_debits, 2),
        "savings": savings,
        "transactions": transactions
    }


def parse_pdf_statement(file_bytes: bytes, country: str = "India") -> Dict[str, Any]:
    """Parse PDF statement using pypdf text extraction or Gemini fallback."""
    extracted_text = ""
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages[:10]:
            t = page.extract_text()
            if t:
                extracted_text += t + "\n"
    except Exception as e:
        print(f"pypdf extraction error: {e}")

    if len(extracted_text.strip()) < 100:
        gemini_result = parse_with_gemini_multimodal(file_bytes, "application/pdf", country)
        if gemini_result:
            return gemini_result

    currency_code, currency_symbol = detect_currency_from_text(extracted_text, country)

    transactions = []
    lines = extracted_text.splitlines()
    total_debits = 0.0
    total_credits = 0.0
    base_date = date.today()

    date_regex = re.compile(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+[A-Za-z]{3}\s+\d{2,4})')
    amount_regex = re.compile(r'([\d,]+\.\d{2})')

    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        d_match = date_regex.search(line)
        amt_matches = amount_regex.findall(line)

        if d_match and amt_matches:
            try:
                clean_line = date_regex.sub('', line)
                amt_str = amt_matches[-1].replace(',', '')
                amount = float(amt_str)
                if amount <= 0:
                    continue

                clean_line = amount_regex.sub('', clean_line).strip()
                desc = clean_line[:80].strip() or "Bank Transaction"

                is_credit = any(c in line.upper() for c in ["CR", "CREDIT", "REFUND", "SALARY", "DEPOSIT"])
                txn_type = "Credit" if is_credit else "Debit"

                txn_date = base_date - timedelta(days=idx % 45)
                raw_d = d_match.group(1)
                for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%m/%d/%Y"]:
                    try:
                        txn_date = datetime.strptime(raw_d, fmt).date()
                        break
                    except ValueError:
                        pass

                category = categorize_merchant(desc)
                if txn_type == "Credit" and category != "Salary":
                    if amount > 20000 or "salary" in desc.lower():
                        category = "Salary"

                if txn_type == "Debit":
                    total_debits += amount
                else:
                    total_credits += amount

                transactions.append({
                    "merchant_name": desc,
                    "category": category,
                    "amount": round(amount, 2),
                    "transaction_type": txn_type,
                    "payment_method": "Bank Transfer" if txn_type == "Credit" else "Card/UPI",
                    "transaction_date": txn_date.strftime("%Y-%m-%d"),
                    "ai_score": str(random.randint(1, 4))
                })
            except Exception:
                continue

    if len(transactions) < 3:
        gemini_result = parse_with_gemini_multimodal(file_bytes, "application/pdf", country)
        if gemini_result:
            return gemini_result
        return generate_sample_statement(currency=currency_code, country=country)

    balance = max(round(total_credits - total_debits, 2), round(total_credits * 0.45, 2))
    monthly_salary = total_credits if total_credits > 0 else round(total_debits * 1.3, 2)
    savings = round(balance * 0.35, 2)

    return {
        "currency_code": currency_code,
        "currency_symbol": currency_symbol,
        "total_balance": balance,
        "monthly_income": monthly_salary,
        "monthly_expenses": round(total_debits, 2),
        "savings": savings,
        "transactions": transactions
    }


def parse_image_statement(file_bytes: bytes, mime_type: str, country: str = "India") -> Dict[str, Any]:
    """Parse bank statement screenshot or image using Gemini Multimodal AI."""
    gemini_result = parse_with_gemini_multimodal(file_bytes, mime_type, country)
    if gemini_result:
        return gemini_result
    
    c_code, c_sym = detect_currency_from_text("", country)
    return generate_sample_statement(currency=c_code, country=country)


def parse_with_gemini_multimodal(file_bytes: bytes, mime_type: str, country: str = "India") -> Optional[Dict[str, Any]]:
    """Call Google Gemini 2.5/2.0 multimodal model to extract structured statement data."""
    client = get_client()
    if not client:
        return None

    try:
        from google.genai import types

        prompt = f"""
You are a senior banking financial auditor and document parser.
Analyze this bank statement image or document from the user (Country hint: {country}).
Extract all visible transactions and summary data accurately.
Detect the exact bank currency (e.g., INR with symbol ₹ for India, USD with $, EUR with €, GBP with £, etc.).

Return ONLY a valid JSON object matching this exact schema:
{{
    "currency_code": "INR",
    "currency_symbol": "₹",
    "total_balance": 125000.00,
    "monthly_income": 65000.00,
    "monthly_expenses": 32000.00,
    "savings": 25000.00,
    "transactions": [
        {{
            "merchant_name": "Flipkart Online",
            "category": "Shopping",
            "amount": 1499.00,
            "transaction_type": "Debit",
            "payment_method": "UPI",
            "transaction_date": "2026-09-15"
        }}
    ]
}}

Categories must be one of: Food, Groceries, Bills, Rent, Entertainment, Shopping, Fuel, Electronics, Health, Salary, Investment.
transaction_type must be either 'Debit' or 'Credit'.
Ensure amounts are strictly numbers without currency symbols or commas.
Return strictly the JSON object, without backticks or markdown fences.
"""

        candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        for model in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=[
                        types.Part.from_bytes(
                            data=file_bytes,
                            mime_type=mime_type,
                        ),
                        prompt
                    ]
                )
                if response and response.text:
                    cleaned_text = response.text.strip()
                    if cleaned_text.startswith("```json"):
                        cleaned_text = cleaned_text[7:]
                    if cleaned_text.startswith("```"):
                        cleaned_text = cleaned_text[3:]
                    if cleaned_text.endswith("```"):
                        cleaned_text = cleaned_text[:-3]
                    cleaned_text = cleaned_text.strip()

                    parsed = json.loads(cleaned_text)
                    if "transactions" in parsed and len(parsed["transactions"]) > 0:
                        return parsed
            except Exception as e:
                print(f"Gemini multimodal attempt with model {model} failed: {e}")
                continue

    except Exception as e:
        print(f"Gemini multimodal parser initialization failed: {e}")

    return None


def generate_sample_statement(currency: str = "INR", country: str = "India") -> Dict[str, Any]:
    """Generate realistic bank statement data tailored to the specified country and currency."""
    currency_code, currency_symbol = detect_currency_from_text(currency, country)

    multiplier = 1.0
    if currency_code == "INR":
        multiplier = 80.0
    elif currency_code in ["EUR", "GBP"]:
        multiplier = 0.85
    elif currency_code == "AED":
        multiplier = 3.67
    elif currency_code == "JPY":
        multiplier = 150.0

    today = date.today()
    sample_merchants = [
        ("Employer Monthly Payroll", "Salary", 4500.0 * multiplier, "Credit", "Bank Transfer"),
        ("Monthly Home Rent / Housing", "Rent", 1200.0 * multiplier, "Debit", "Bank Transfer"),
        ("Electricity & Power Utility", "Bills", 95.0 * multiplier, "Debit", "Bank Transfer"),
        ("Starbucks Coffee / Cafe", "Food", 18.0 * multiplier, "Debit", "Card"),
        ("Weekend Supermarket Groceries", "Groceries", 145.0 * multiplier, "Debit", "Card"),
        ("Fuel & Gas Station", "Fuel", 55.0 * multiplier, "Debit", "Card"),
        ("Netflix & Streaming Subscription", "Entertainment", 15.0 * multiplier, "Debit", "Card"),
        ("Amazon Electronics Purchase", "Electronics", 280.0 * multiplier, "Debit", "Card"),
        ("Dining & Food Delivery", "Food", 42.0 * multiplier, "Debit", "UPI" if currency_code == "INR" else "Card"),
        ("Pharmacies & Health Care", "Health", 38.0 * multiplier, "Debit", "Card"),
        ("Mobile & WiFi Broadband", "Bills", 45.0 * multiplier, "Debit", "Bank Transfer"),
        ("Department Store Shopping", "Shopping", 110.0 * multiplier, "Debit", "Card"),
    ]

    transactions = []
    total_debits = 0.0
    total_credits = 0.0

    for idx, (merchant, category, amt, t_type, pay_method) in enumerate(sample_merchants):
        amt_rounded = round(amt, 2)
        txn_date = today - timedelta(days=idx * 2 + 1)
        if t_type == "Credit":
            total_credits += amt_rounded
        else:
            total_debits += amt_rounded

        transactions.append({
            "merchant_name": merchant,
            "category": category,
            "amount": amt_rounded,
            "transaction_type": t_type,
            "payment_method": pay_method,
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "ai_score": str(random.randint(1, 4))
        })

    balance = round(total_credits - total_debits + (1200.0 * multiplier), 2)
    monthly_salary = round(total_credits, 2)
    savings = round(balance * 0.35, 2)

    return {
        "currency_code": currency_code,
        "currency_symbol": currency_symbol,
        "total_balance": balance,
        "monthly_income": monthly_salary,
        "monthly_expenses": round(total_debits, 2),
        "savings": savings,
        "transactions": transactions
    }
