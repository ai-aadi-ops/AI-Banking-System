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

# Maximum monthly EMI allowed in this demo
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
    product="Personal Loan"
):
    """
    Select the shortest available tenure where
    the calculated EMI is within the maximum
    affordable EMI limit.

    Demo rule:
        Maximum EMI = $2,000/month

    Personal loans:
        Up to 6 years

    Home loans:
        Up to 30 years
    """

    loan_amount = float(loan_amount)
    monthly_salary = float(monthly_salary)

    interest_rate, tenure_options = (
        get_loan_configuration(product)
    )

    # Maximum EMI allowed by the demo
    max_affordable_emi = MAX_EMI_AMOUNT

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

    # Even the longest available tenure
    # exceeds the maximum EMI.
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

    # Even the longest tenure is above
    # preferred affordability limit.
    tenure = tenure_options[-1]

    emi = calculate_emi(
        loan_amount,
        interest_rate,
        tenure
    )

    return tenure, emi, interest_rate, False


# =========================================================
# PURCHASE DETAILS EXTRACTION
# =========================================================

def extract_purchase_details(question: str):
    """
    Extract purchase amount and product from
    natural-language questions.

    Supported amount formats:

        $25,000
        $25000
        25000$
        25,000$
        25000 dollars
        25000 dollar
        25000 USD

    Examples:

        Can I buy a laptop worth $25,000?
        Can I afford an iPhone for $8,000?
        Can I purchase a car worth 30000$?
        Can I buy a house worth $100000?
        Can I buy a house worth 100000 dollars?
    """

    if not question:
        return None, "Purchase", "AI Partner Store"

    # =====================================================
    # EXTRACT AMOUNT
    # =====================================================

    amount_match = re.search(
        r"(?:"
        r"\$\s*([0-9][0-9,]*(?:\.[0-9]+)?)"
        r"|"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)\s*\$"
        r"|"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)"
        r"\s*(?:dollars?|usd)"
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

            amount = float(
                raw_amount.replace(",", "")
            )

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
        ]
    ):
        product = "iPhone"
        merchant = "Apple Demo Store"

    # House / Home / Property
    elif any(
        word in question_lower
        for word in [
            "house",
            "home",
            "property",
            "real estate",
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
    product="Personal Loan"
):
    """
    Create a dynamically calculated loan offer.

    The requested loan amount is treated as the
    actual loan principal.

    A loan offer is generated only when the
    calculated EMI is <= $2,000/month.
    """

    balance = float(balance)
    amount = float(amount)
    monthly_salary = float(monthly_salary)

    # =========================================================
    # BASIC VALIDATION
    # =========================================================

    if amount <= 0:
        return None

    # =========================================================
    # DETERMINE LOAN TYPE
    # =========================================================

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

    # =========================================================
    # CALCULATE TENURE + EMI
    # =========================================================

    (
        tenure,
        monthly_emi,
        interest_rate,
        emi_affordable
    ) = select_loan_tenure(
        amount,
        monthly_salary,
        product
    )

    # =========================================================
    # DO NOT GENERATE OFFER IF EMI IS TOO HIGH
    # =========================================================

    if not emi_affordable:
        return None

    # =========================================================
    # HUMAN-READABLE TENURE
    # =========================================================

    tenure_years = tenure / 12

    if tenure_years.is_integer():

        tenure_display = (
            f"{int(tenure_years)} years"
        )

    else:

        tenure_display = (
            f"{tenure} months"
        )

    # =========================================================
    # RETURN LOAN OFFER
    # =========================================================

    return {

        "type": "loan",

        "title": title,

        "product": (
            f"Pre-approved {loan_name}"
        ),

        "merchant": (
            "AI Banking Credit Desk"
        ),

        "amount": round(
            amount,
            2
        ),

        "monthly_emi": monthly_emi,

        "tenure_months": tenure,

        "interest_rate": interest_rate,

        "discount_percent": 0,

        "loan_type": loan_name,

        "reason": (

            f"AI has evaluated a "
            f"{loan_name.lower()} of "
            f"${amount:,.2f} at "
            f"{interest_rate}% annual interest. "

            f"The estimated monthly EMI is "
            f"${monthly_emi:,.2f} for "
            f"{tenure_display}. "

            f"This EMI is within the demo "
            f"maximum EMI limit of "
            f"${MAX_EMI_AMOUNT:,.2f} per month."
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
    merchant
):
    """
    Create a product-specific purchase offer.

    Normal purchase offers do NOT contain EMI.
    """

    discount_percent = 10

    discounted_price = round(
        amount
        * (
            1 - discount_percent / 100
        ),
        2
    )

    return {

        "type": "purchase",

        "title": (
            f"{product} Purchase Offer"
        ),

        "product": (
            f"Premium {product}"
        ),

        "merchant": merchant,

        "original_price": round(
            amount,
            2
        ),

        "discounted_price": (
            discounted_price
        ),

        "amount": discounted_price,

        "monthly_emi": 0,

        "tenure_months": 0,

        "interest_rate": 0,

        "discount_percent": (
            discount_percent
        ),

        "reason": (

            f"Your available balance is "
            f"${balance:,.2f}, which is sufficient "
            f"for the requested "
            f"${amount:,.2f} "
            f"{product.lower()}. "

            f"AI found a "
            f"{discount_percent}% "
            f"demo discount offer."
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
    question
):
    """
    Decide whether an offer should be generated.

    Rules:

    1. Explicit loan question
       -> Personal Loan Offer

    2. Purchase + recognized product
       -> Purchase Offer OR Loan Offer

    3. Unrelated question
       -> No Offer
    """

    balance = float(
        account.balance
    )

    monthly_salary = float(
        customer.salary
    )

    q = (
        question or ""
    ).lower()

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
    ]

    has_loan_intent = any(
        word in q
        for word in loan_keywords
    )

    if has_loan_intent:

        # Detect whether this is a home loan
        is_home_loan = any(
            word in q
            for word in [
                "home loan",
                "house loan",
                "mortgage",
                "home",
                "house",
                "property",
            ]
        )

        product = (
            "House"
            if is_home_loan
            else "Personal Loan"
        )

        # If user mentions an amount,
        # use that amount. Otherwise use demo amount.
        amount_match = re.search(
            r"(?:"
            r"\$\s*([0-9][0-9,]*(?:\.[0-9]+)?)"
            r"|"
            r"([0-9][0-9,]*(?:\.[0-9]+)?)\s*\$"
            r"|"
            r"([0-9][0-9,]*(?:\.[0-9]+)?)"
            r"\s*(?:dollars?|usd)"
            r")",
            q,
            re.IGNORECASE
        )

        loan_amount = None

        if amount_match:

            try:

                raw_amount = (
                    amount_match.group(1)
                    or amount_match.group(2)
                    or amount_match.group(3)
                )

                loan_amount = float(
                    raw_amount.replace(",", "")
                )

            except (
                ValueError,
                TypeError
            ):
                loan_amount = None

        if loan_amount is None:
            # No specific loan amount was requested.
            # Provide AI advice only.
            return None

        return build_loan_offer(
            balance,
            loan_amount,
            monthly_salary,
            product
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
    ]

    product_keywords = [

        # Phones
        "iphone",
        "i phone",
        "ipad",
        "phone",
        "smartphone",
        "mobile",

        # Computers
        "laptop",
        "computer",
        "macbook",
        "notebook",
        "pc",

        # Vehicles
        "car",
        "vehicle",
        "suv",
        "bike",
        "motorcycle",
        "scooter",

        # Home
        "house",
        "home",
        "property",
        "real estate",

        # Electronics
        "tv",
        "television",
    ]

    has_purchase_keyword = any(
        word in q
        for word in purchase_keywords
    )

    has_product = any(
        word in q
        for word in product_keywords
    )

    # =====================================================
    # NO OFFER FOR UNRELATED QUESTIONS
    # =====================================================

    if not (
        has_purchase_keyword
        and has_product
    ):
        return None


    # =====================================================
    # EXTRACT PURCHASE DETAILS
    # =====================================================

    (
        purchase_amount,
        product,
        merchant
    ) = extract_purchase_details(q)

    # =====================================================
    # DEFAULT PRODUCT PRICES
    # =====================================================

    if purchase_amount is None:

        if product == "iPhone":
            purchase_amount = 7790.00

        elif product == "Laptop":
            purchase_amount = 25000.00

        elif product == "Car":
            purchase_amount = 40000.00

        elif product == "House":
            purchase_amount = 100000.00

        else:
            return None

    # =====================================================
    # PURCHASE EXCEEDS BALANCE
    # -> LOAN OFFER
    # =====================================================

    if purchase_amount > balance:

        required_loan = (
        purchase_amount - balance
        )

        return build_loan_offer(
            balance,
            purchase_amount,
            monthly_salary,
            product
        )

    # =====================================================
    # PURCHASE IS AFFORDABLE
    # -> PRODUCT OFFER
    # =====================================================

    return build_purchase_offer(
        balance,
        purchase_amount,
        product,
        merchant
    )
