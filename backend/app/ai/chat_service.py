from app.ai.gemini_service import ask_gemini


def chat_with_ai(
    customer,
    account,
    spending,
    health,
    question,
):

    prompt = f"""
You are an AI Banking Assistant.

Customer:
{customer.full_name}

Annual Salary:
{customer.salary}

Current Balance:
{account.balance}

Savings:
{account.savings}

Financial Health:
{health["financial_health_score"]}

Status:
{health["status"]}

Highest Spending Category:
{spending["highest_spending_category"]}

Category Breakdown:
{spending["category_breakdown"]}

Customer Question:
{question}

Answer as an experienced banking financial advisor.

Give practical advice.

Maximum 200 words.
"""

    return ask_gemini(prompt)
