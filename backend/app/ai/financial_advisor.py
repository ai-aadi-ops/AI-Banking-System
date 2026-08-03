from app.ai.gemini_service import ask_gemini


def generate_financial_advice(
    customer,
    account,
    spending,
    health
):

    prompt = f"""
You are an expert AI Financial Advisor.

Customer Name:
{customer.full_name}

Annual Salary:
{customer.salary}

Current Account Balance:
{account.balance}

Savings:
{account.savings}

Financial Health Score:
{health["financial_health_score"]}

Status:
{health["status"]}

Highest Spending Category:
{spending["highest_spending_category"]}

Category Breakdown:
{spending["category_breakdown"]}

Analyze this customer and provide:

1. Spending summary
2. Savings advice
3. Investment advice
4. Loan advice
5. Credit card advice
6. Risk level
7. Final recommendation

Keep the response under 250 words.
"""

    return ask_gemini(prompt)
