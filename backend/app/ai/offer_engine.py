import re


DEMO_BASE_BALANCE = 20000.00
LOW_BALANCE_THRESHOLD = 5000.00


def extract_purchase_details(question: str):
    """
    Extract purchase amount and product from a natural-language question.

    Examples:
    - Can I buy a laptop worth $25,000 this month?
    - Can I afford an iPhone for $8,000?
    - Can I purchase a car worth $30,000?
    """

    if not question:
        return None, "product"

    # Extract dollar amount
    amount_match = re.search(
        r"\$\s*([0-9][0-9,]*(?:\.[0-9]+)?)",
        question
    )

    amount = None

    if amount_match:
        try:
            amount = float(amount_match.group(1).replace(",", ""))
        except ValueError:
            amount = None

    # Detect product/category
    question_lower = question.lower()

    if any(word in question_lower for word in [
        "laptop",
        "macbook",
        "computer",
        "pc"
    ]):
        product = "Laptop"
        merchant = "AI Electronics Store"

    elif any(word in question_lower for word in [
        "iphone",
        "ipad",
        "apple phone"
    ]):
        product = "iPhone"
        merchant = "Apple Demo Store"

    elif any(word in question_lower for word in [
        "car",
        "vehicle",
        "automobile",
        "suv"
    ]):
        product = "Car"
        merchant = "AI Auto Marketplace"

    elif any(word in question_lower for word in [
        "phone",
        "smartphone",
        "mobile"
    ]):
        product = "Smartphone"
        merchant = "AI Mobile Store"

    elif any(word in question_lower for word in [
        "tv",
        "television"
    ]):
        product = "Smart TV"
        merchant = "AI Electronics Store"

    elif any(word in question_lower for word in [
        "bike",
        "motorcycle",
        "scooter"
    ]):
        product = "Two-Wheeler"
        merchant = "AI Auto Marketplace"

    else:
        product = "Purchase"
        merchant = "AI Partner Store"

    return amount, product, merchant


def build_loan_offer(balance, amount):
    """
    Create a loan offer when requested purchase exceeds
    available account balance.
    """

    shortfall = max(0.0, amount - balance)

    # Keep the demo's minimum loan amount.
    loan_amount = max(15000.00, shortfall)

    return {
        "type": "loan",
        "title": "Instant Personal Loan Offer",
        "product": "Pre-approved Personal Loan",
        "merchant": "AI Banking Credit Desk",
        "amount": loan_amount,
        "monthly_emi": 1381.25,
        "tenure_months": 12,
        "interest_rate": 10.5,
        "discount_percent": 0,
        "reason": (
            f"Your available balance is ${balance:,.2f}, "
            f"but the requested purchase is ${amount:,.2f}. "
            f"You need an additional ${shortfall:,.2f}. "
            "AI recommends a personal loan instead of allowing "
            "the account balance to go negative."
        ),
        "cta": "Accept Loan Offer",
    }


def build_purchase_offer(balance, amount, product, merchant):
    """
    Create a purchase-specific demo offer.

    No EMI/monthly deduction is included because this is
    a normal purchase/discount offer, not a loan.
    """

    # Demo discount for affordable purchases.
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
        "original_price": amount,
        "discounted_price": discounted_price,
        "amount": discounted_price,
        "monthly_emi": 0,
        "tenure_months": 0,
        "interest_rate": 0,
        "discount_percent": discount_percent,
        "reason": (
            f"Your available balance is ${balance:,.2f}, "
            f"which is sufficient for the requested ${amount:,.2f} "
            f"{product.lower()}. AI found a {discount_percent}% "
            "demo discount offer."
        ),
        "cta": "Accept Discount Offer",
    }


def build_default_offer(balance):
    """
    Default demo offer when the user did not specify
    a purchase amount.
    """

    return {
        "type": "purchase",
        "title": "iPhone Upgrade Offer",
        "product": "iPhone 15 Pro Max Family Bundle",
        "merchant": "Apple Demo Store",
        "original_price": 9500.00,
        "discounted_price": 7790.00,
        "amount": 7790.00,
        "monthly_emi": 0,
        "tenure_months": 0,
        "interest_rate": 0,
        "discount_percent": 18,
        "reason": (
            f"Your balance is ${balance:,.2f}. "
            "AI found an 18% discount offer."
        ),
        "cta": "Accept Discount Offer",
    }

def build_offer(customer, account, spending, health, question):
    balance = float(account.balance)

    question_lower = (question or "").lower()

    purchase_keywords = [
        "buy",
        "purchase",
        "afford",
        "spend",
        "laptop",
        "iphone",
        "ipad",
        "phone",
        "smartphone",
        "mobile",
        "car",
        "vehicle",
        "suv",
        "bike",
        "motorcycle",
        "scooter",
        "tv",
        "television",
        "computer",
        "macbook",
    ]

    loan_keywords = [
        "loan",
        "borrow",
        "financing",
        "finance",
        "emi",
        "installment",
    ]

    has_purchase_intent = any(
        keyword in question_lower
        for keyword in purchase_keywords
    )

    has_loan_intent = any(
        keyword in question_lower
        for keyword in loan_keywords
    )

    # No financial product/purchase intent.
    # Do not show any offer card.
    if not has_purchase_intent and not has_loan_intent:
        return None

    purchase_amount, product, merchant = extract_purchase_details(question)

    # Explicit purchase amount
    if purchase_amount is not None:

        if purchase_amount > balance:
            return build_loan_offer(
                balance,
                purchase_amount
            )

        return build_purchase_offer(
            balance,
            purchase_amount,
            product,
            merchant
        )

    # Explicit loan-related question
    if has_loan_intent:
        return build_loan_offer(
            balance,
            15000.00
        )

    # Low balance + purchase/product question
    if balance <= LOW_BALANCE_THRESHOLD:
        return {
            "type": "loan",
            "title": "Instant Personal Loan Offer",
            "product": "Pre-approved Personal Loan",
            "merchant": "AI Banking Credit Desk",
            "amount": 15000.00,
            "monthly_emi": 1381.25,
            "tenure_months": 12,
            "interest_rate": 10.5,
            "discount_percent": 0,
            "reason": (
                f"Your balance is ${balance:,.2f}, "
                "so AI recommends a loan offer."
            ),
            "cta": "Accept Loan Offer",
        }

    # Product question without explicit amount
    return build_default_offer(balance)
