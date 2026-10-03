import re


# =========================================================
# DEMO CONFIGURATION
# =========================================================

DEMO_BASE_BALANCE = 20000.00
LOW_BALANCE_THRESHOLD = 5000.00

# =========================================================
# LOAN CONFIGURATION
# =========================================================

# Personal loan
PERSONAL_LOAN_INTEREST_RATE = 10.5

# Home loan
HOME_LOAN_INTEREST_RATE = 7.5

# Maximum monthly EMI allowed in this demo (base USD)
MAX_EMI_AMOUNT = 2000.00

# Maximum preferred EMI as percentage of monthly salary
MAX_EMI_PERCENT_OF_SALARY = 0.25


# Personal loan repayment periods
PERSONAL_LOAN_TENURES = [
    12,    # 1 year
    18,    # 1.5 years
    24,    # 2 years
    36,    # 3 years
    48,    # 4 years
    60,    # 5 years
    72,    # 6 years
]


# Home loan repayment periods
HOME_LOAN_TENURES = [
    120,   # 10 years
    180,   # 15 years
    240,   # 20 years
    300,   # 25 years
    360,   # 30 years
]


# =========================================================
# EMI CALCULATION
# =========================================================

def calculate_emi(
    principal,
    annual_interest_rate,
    tenure_months
):
    """
    Calculate EMI using the standard
    reducing-balance formula.
    """

    principal = float(principal)
    annual_interest_rate = float(annual_interest_rate)
    tenure_months = int(tenure_months)

    if principal <= 0 or tenure_months <= 0:
        return 0.0

    monthly_rate = (
        annual_interest_rate / 100 / 12
    )

    # Zero-interest case
    if monthly_rate == 0:
        return round(
            principal / tenure_months,
            2
        )

    emi = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** tenure_months
        / (
            (1 + monthly_rate) ** tenure_months
            - 1
        )
    )

    return round(emi, 2)


# =========================================================
# LOAN TYPE CONFIGURATION
# =========================================================

def get_loan_configuration(product):
    """
    Return interest rate and available tenures
    based on the requested product.

    House -> Home Loan
    Everything else -> Personal Loan
    """

    if product == "House":
        return (
            HOME_LOAN_INTEREST_RATE,
            HOME_LOAN_TENURES
        )

    return (
        PERSONAL_LOAN_INTEREST_RATE,
        PERSONAL_LOAN_TENURES
    )


# =========================================================
# TENURE SELECTION
# =========================================================

def select_loan_tenure(
    loan_amount,
    monthly_salary,
    product="Personal Loan",
    currency_symbol="$"
):
    """
    Select the shortest available tenure where
    the calculated EMI is within the maximum
    affordable EMI limit.
    """

    loan_amount = float(loan_amount)
    monthly_salary = float(monthly_salary)

    interest_rate, tenure_options = (
        get_loan_configuration(product)
    )

    # Scale max EMI limit for INR vs USD
    base_max = 50000.0 if currency_symbol == "₹" else MAX_EMI_AMOUNT
    max_affordable_emi = max(base_max, monthly_salary * 0.5) if monthly_salary > 0 else base_max

    # Try shortest tenure first
    for tenure in tenure_options:

        emi = calculate_emi(
            loan_amount,
            interest_rate,
            tenure
        )

        if emi <= max_affordable_emi:
            return (
                tenure,
                emi,
                interest_rate,
                True
            )

    # Even the longest available tenure exceeds the maximum EMI.
    tenure = tenure_options[-1]

    emi = calculate_emi(
        loan_amount,
        interest_rate,
        tenure
    )

    return (
        tenure,
        emi,
        interest_rate,
        False
    )


# =========================================================
# PURCHASE DETAILS EXTRACTION
# =========================================================

def extract_purchase_details(question: str):
    """
    Extract purchase amount and product from
    natural-language questions in any currency ($, ₹, £, €, etc.).
    """

    if not question:
        return None, "Purchase", "AI Partner Store"

    # =====================================================
    # EXTRACT AMOUNT
    # =====================================================

    amount_match = re.search(
        r"(?:"
        r"(?:\$|₹|rs\.?|inr|usd|€|£)\s*([0-9][0-9,]*(?:\.[0-9]+)?)"
        r"|"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:\$|₹|rs\.?|inr|usd|€|£|dollars?|rupees?)"
        r"|"
        r"(?:worth|for|of)\s+([0-9][0-9,]*(?:\.[0-9]+)?)"
        r")",
        question,
        re.IGNORECASE
    )

    amount = None

    if amount_match:
        try:
            raw_amount = (
                amount_match.group(1)
                or amount_match.group(2)
                or amount_match.group(3)
            )
            amount = float(raw_amount.replace(",", ""))
        except (ValueError, TypeError):
            amount = None

    # =====================================================
    # PRODUCT DETECTION
    # =====================================================

    question_lower = question.lower()

    # Laptop
    if any(
        word in question_lower
        for word in [
            "laptop",
            "macbook",
            "computer",
            "notebook",
            "pc",
            "लैपटॉप",
        ]
    ):
        product = "Laptop"
        merchant = "AI Electronics Store"

    # Phone / iPhone
    elif any(
        word in question_lower
        for word in [
            "iphone",
            "i phone",
            "phone",
            "smartphone",
            "mobile",
            "स्मार्टफोन",
            "फोन",
            "मोबाइल",
        ]
    ):
        product = "Smartphone" if "smartphone" in question_lower or "स्मार्टफोन" in question_lower else "iPhone"
        merchant = "Apple Demo Store"

    # House / Home / Property
    elif any(
        word in question_lower
        for word in [
            "house",
            "home",
            "property",
            "real estate",
            "घर",
            "मकान",
        ]
    ):
        product = "House"
        merchant = "AI Real Estate Marketplace"

    # Car
    elif any(
        word in question_lower
        for word in [
            "car",
            "vehicle",
            "automobile",
            "suv",
            "कार",
            "गाड़ी",
        ]
    ):
        product = "Car"
        merchant = "AI Auto Marketplace"

    # Bike
    elif any(
        word in question_lower
        for word in [
            "bike",
            "motorcycle",
            "scooter",
            "बाइक",
        ]
    ):
        product = "Two-Wheeler"
        merchant = "AI Auto Marketplace"

    # TV
    elif any(
        word in question_lower
        for word in [
            "tv",
            "television",
            "टीवी",
        ]
    ):
        product = "Smart TV"
        merchant = "AI Electronics Store"

    else:
        product = "Purchase"
        merchant = "AI Partner Store"

    return amount, product, merchant


# =========================================================
# LOAN OFFER
# =========================================================

def build_loan_offer(
    balance,
    amount,
    monthly_salary,
    product="Personal Loan",
    currency_symbol="$"
):
    """
    Create a dynamically calculated loan offer.
    """

    balance = float(balance)
    amount = float(amount)
    monthly_salary = float(monthly_salary)

    if amount <= 0:
        return None

    is_home_loan = product == "House"

    loan_name = (
        "Home Loan"
        if is_home_loan
        else "Personal Loan"
    )

    title = (
        "Personalized Home Loan Offer"
        if is_home_loan
        else "Instant Personal Loan Offer"
    )

    (
        tenure,
        monthly_emi,
        interest_rate,
        emi_affordable
    ) = select_loan_tenure(
        amount,
        monthly_salary,
        product,
        currency_symbol=currency_symbol
    )

    if not emi_affordable:
        return None

    tenure_years = tenure / 12

    if tenure_years.is_integer():
        tenure_display = f"{int(tenure_years)} years"
    else:
        tenure_display = f"{tenure} months"

    return {
        "type": "loan",
        "title": title,
        "product": f"Pre-approved {loan_name}",
        "merchant": "AI Banking Credit Desk",
        "amount": round(amount, 2),
        "monthly_emi": monthly_emi,
        "tenure_months": tenure,
        "interest_rate": interest_rate,
        "discount_percent": 0,
        "loan_type": loan_name,
        "reason": (
            f"AI has evaluated a {loan_name.lower()} of "
            f"{currency_symbol}{amount:,.2f} at "
            f"{interest_rate}% annual interest. "
            f"The estimated monthly EMI is "
            f"{currency_symbol}{monthly_emi:,.2f} for "
            f"{tenure_display}."
        ),
        "cta": "Accept Loan Offer",
    }


# =========================================================
# PURCHASE OFFER
# =========================================================

def build_purchase_offer(
    balance,
    amount,
    product,
    merchant,
    currency_symbol="$"
):
    """
    Create a product-specific purchase offer.
    """

    discount_percent = 10

    discounted_price = round(
        amount * (1 - discount_percent / 100),
        2
    )

    return {
        "type": "purchase",
        "title": f"{product} Purchase Offer",
        "product": f"Premium {product}",
        "merchant": merchant,
        "original_price": round(amount, 2),
        "discounted_price": discounted_price,
        "amount": discounted_price,
        "monthly_emi": 0,
        "tenure_months": 0,
        "interest_rate": 0,
        "discount_percent": discount_percent,
        "reason": (
            f"Your available balance is "
            f"{currency_symbol}{balance:,.2f}, which is sufficient "
            f"for the requested "
            f"{currency_symbol}{amount:,.2f} "
            f"{product.lower()}. "
            f"AI found a {discount_percent}% "
            f"partner discount offer."
        ),
        "cta": "Accept Discount Offer",
    }


# =========================================================
# MAIN OFFER ENGINE
# =========================================================

def build_offer(
    customer,
    account,
    spending,
    health,
    question,
    currency_symbol="$"
):
    """
    Decide whether an offer should be generated.
    """

    balance = float(account.balance) if account and account.balance else 0.0
    monthly_salary = (
        float(account.monthly_salary)
        if account and getattr(account, "monthly_salary", 0)
        else (float(customer.salary) if customer and customer.salary else 0.0)
    )

    q = (question or "").lower()

    # =====================================================
    # EXPLICIT LOAN INTENT
    # =====================================================

    loan_keywords = [
        "loan",
        "borrow",
        "financing",
        "finance",
        "emi",
        "installment",
        "personal loan",
        "home loan",
        "mortgage",
        "ऋण",
        "लोन",
    ]

    has_loan_intent = any(
        word in q
        for word in loan_keywords
    )

    if has_loan_intent:
        is_home_loan = any(
            word in q
            for word in [
                "home loan",
                "house loan",
                "mortgage",
                "home",
                "house",
                "property",
                "होम लोन",
                "घर",
            ]
        )

        product = "House" if is_home_loan else "Personal Loan"

        amount_match = re.search(
            r"(?:"
            r"(?:\$|₹|rs\.?|inr|usd|€|£)\s*([0-9][0-9,]*(?:\.[0-9]+)?)"
            r"|"
            r"([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:\$|₹|rs\.?|inr|usd|€|£|dollars?|rupees?)"
            r")",
            q,
            re.IGNORECASE
        )

        loan_amount = None

        if amount_match:
            try:
                raw_amount = amount_match.group(1) or amount_match.group(2)
                loan_amount = float(raw_amount.replace(",", ""))
            except (ValueError, TypeError):
                loan_amount = None

        if loan_amount is None:
            return None

        return build_loan_offer(
            balance,
            loan_amount,
            monthly_salary,
            product,
            currency_symbol=currency_symbol
        )

    # =====================================================
    # PURCHASE INTENT
    # =====================================================

    purchase_keywords = [
        "buy",
        "purchase",
        "afford",
        "worth",
        "cost",
        "item",
        # Hindi / Hinglish
        "kharid",
        "khareed",
        "khreed",
        "khareedna",
        "kharidna",
        "le sakta",
        "le sakti",
        "le sakte",
        "le sakta hun",
        "le sakta hoon",
        "le lu",
        "lelo",
        "lena hai",
        "lena chahta",
        "lena chahti",
        "खरीद",
        "ले सकता",
        "ले सकती",
    ]

    product_keywords = [
        "iphone",
        "i phone",
        "ipad",
        "phone",
        "smartphone",
        "mobile",
        "item",
        "laptop",
        "computer",
        "macbook",
        "notebook",
        "pc",
        "car",
        "vehicle",
        "suv",
        "bike",
        "motorcycle",
        "scooter",
        "house",
        "home",
        "property",
        "real estate",
        "tv",
        "television",
        "स्मार्टफोन",
        "लैपटॉप",
        "फोन",
        "कार",
        "घर",
    ]

    has_purchase_keyword = any(word in q for word in purchase_keywords)
    has_product = any(word in q for word in product_keywords)

    if not (has_purchase_keyword and has_product):
        return None

    (
        purchase_amount,
        product,
        merchant
    ) = extract_purchase_details(q)

    if purchase_amount is None:
        mult = 80.0 if currency_symbol == "₹" else 1.0
        if product in ("iPhone", "Smartphone"):
            purchase_amount = 1000.00 * mult
        elif product == "Laptop":
            purchase_amount = 1500.00 * mult
        elif product == "Car":
            purchase_amount = 25000.00 * mult
        elif product == "House":
            purchase_amount = 100000.00 * mult
        else:
            return None

    if purchase_amount > balance:
        return build_loan_offer(
            balance,
            purchase_amount,
            monthly_salary,
            product,
            currency_symbol=currency_symbol
        )

    return build_purchase_offer(
        balance,
        purchase_amount,
        product,
        merchant,
        currency_symbol=currency_symbol
    )
