from app.ai.gemini_service import ask_gemini
from app.ai.offer_engine import MAX_EMI_AMOUNT

def chat_with_ai(
    customer,
    account,
    spending,
    health,
    question,
    offer=None,
    currency_symbol="$",
    language="en",
):
    monthly_salary = float(customer.salary) if customer and customer.salary else 0.0
    annual_salary = monthly_salary * 12

    current_balance = float(account.balance) if account and account.balance else 0.0
    savings = float(account.savings) if account and account.savings else 0.0

    # Prepare personalized offer information for the AI
    if offer:
        offer_type = offer.get("type", "unknown")

        if offer_type == "loan":
            offer_information = f"""
Personalized Offer Type: PERSONAL LOAN

Loan Amount:
{currency_symbol}{float(offer.get("amount", 0)):,.2f}

Monthly EMI / Deduction:
{currency_symbol}{float(offer.get("monthly_emi", 0)):,.2f}

Tenure:
{offer.get("tenure_months", 0)} months

Interest Rate:
{offer.get("interest_rate", 0)}%

Reason:
{offer.get("reason", "")}
"""

        elif offer_type == "purchase":
            offer_information = f"""
Personalized Offer Type: PURCHASE

Product:
{offer.get("product", "")}

Merchant:
{offer.get("merchant", "")}

Original Price:
{currency_symbol}{float(offer.get("original_price", offer.get("amount", 0))):,.2f}

Purchase Amount:
{currency_symbol}{float(offer.get("amount", 0)):,.2f}

Discount:
{offer.get("discount_percent", 0)}%

Reason:
{offer.get("reason", "")}
"""


        else:
            offer_information = "No valid personalized offer is available."

    else:
        offer_information = f"""
No personalized offer is currently available.

LOAN ELIGIBILITY RULE:
The maximum allowed monthly EMI for this demo is {currency_symbol}{MAX_EMI_AMOUNT:,.2f}.

If the requested loan results in a monthly EMI above
{currency_symbol}{MAX_EMI_AMOUNT:,.2f}, the loan is NOT eligible.

The AI Advisor must clearly explain that the requested loan
cannot currently be offered because the calculated EMI exceeds
the maximum affordability threshold of {currency_symbol}{MAX_EMI_AMOUNT:,.2f}
per month.

Advise the customer to consider a lower loan amount,
a larger down payment, or a more affordable financing option.

Do not present a rejected loan as an available or pre-approved offer.
"""

    lang_map = {
        "hi": "Hindi (हिंदी)",
        "bn": "Bengali (বাংলা)",
        "te": "Telugu (తెలుగు)",
        "mr": "Marathi (मराठी)",
        "ta": "Tamil (தமிழ்)",
        "gu": "Gujarati (ગુજરાતી)",
        "kn": "Kannada (ಕನ್ನಡ)",
        "ml": "Malayalam (മലയാളം)",
        "pa": "Punjabi (ਪੰਜਾਬੀ)",
        "en": "English",
    }
    lang_name = lang_map.get(language.lower(), "English")

    prompt = f"""
You are an AI Banking Financial Advisor for an intelligent banking platform.

CUSTOMER PROFILE
----------------
Customer Name: {customer.full_name}
Currency Symbol: {currency_symbol}
Preferred Language: {lang_name}

Monthly Salary:
{currency_symbol}{monthly_salary:,.2f}

Annual Salary:
{currency_symbol}{annual_salary:,.2f}

IMPORTANT SALARY RULE:
The salary value stored in the database is MONTHLY salary.
Always describe {currency_symbol}{monthly_salary:,.2f} as the customer's MONTHLY salary.
Never describe {currency_symbol}{monthly_salary:,.2f} as the annual salary.
The customer's annual salary is {currency_symbol}{annual_salary:,.2f}.

CURRENT FINANCIAL POSITION
--------------------------
Current Account Balance:
{currency_symbol}{current_balance:,.2f}

Savings:
{currency_symbol}{savings:,.2f}

Financial Health Score:
{health["financial_health_score"]}

Financial Health Status:
{health["status"]}

SPENDING ANALYSIS
-----------------
Highest Spending Category:
{spending["highest_spending_category"]}

Category Breakdown:
{spending["category_breakdown"]}

PERSONALIZED OFFER
------------------
{offer_information}

CUSTOMER QUESTION
-----------------
{question}

INSTRUCTIONS
------------
1. Act as a trusted, warm, and highly experienced banking financial advisor.
2. Answer the customer's question directly and naturally using their real numbers.
3. Use the currency symbol '{currency_symbol}' for all amounts. Never switch to '$' if currency is '{currency_symbol}'.
4. LANGUAGE REQUIREMENT: You MUST answer in {lang_name}. If {lang_name} is Hindi, respond in fluent Hindi. If English, respond in English. If bilingual Hinglish question, respond in friendly, professional Hinglish.


IMPORTANT OFFER RULES:

1. Only mention the personalized offer if it is relevant to the customer's
   question.

2. Do NOT mention an unrelated offer.

3. If the customer asks about a product or purchase and a relevant purchase
   offer exists, explain the purchase offer naturally.

4. If the customer is asking about a purchase but their balance is too low
   and the personalized offer is a loan, explain that the purchase cannot
   safely be funded from the current balance and mention the available loan
   option.

5. If the customer asks about a loan or financing, mention the loan offer
   when one is available.

6. If there is no relevant personalized offer, do not invent one.

7. Never invent product prices, discounts, loan amounts, EMI values,
   interest rates or tenure.

8. If the offer is a PERSONAL LOAN, mention the relevant:
   - Loan amount
   - Monthly EMI / deduction
   - Tenure
   - Interest rate

9. If the offer is a PURCHASE offer, mention the relevant:
   - Product
   - Purchase amount
   - Discount, if applicable

10. Do not create a payment link or checkout link.

11. Do not claim that a demo offer is a real bank-approved financial product.

12. Give practical financial advice based on the customer's balance,
    savings, salary, spending and financial health.

Maximum 200 words.
"""

    return ask_gemini(prompt)
