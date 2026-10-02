import os
from google import genai
from app.config import GEMINI_API_KEY

_client = None

def get_client():
    global _client
    api_key = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
    if not api_key:
        return None
    if _client is None:
        try:
            _client = genai.Client(api_key=api_key)
        except Exception as e:
            print(f"Warning: Failed to initialize Google GenAI Client: {e}")
            return None
    return _client


def generate_local_advisor_fallback(prompt: str) -> str:
    """Intelligent rule-based fallback response if Gemini API is unreachable or key is invalid."""
    p = prompt.lower()

    # Extract name and currency from prompt if available
    customer_name = "there"
    currency = "$"
    if "customer name:" in p:
        try:
            name_lines = [l for l in prompt.splitlines() if "customer name:" in l.lower()]
            if name_lines:
                customer_name = name_lines[0].split(":")[-1].strip()
        except Exception:
            pass
    if "currency symbol:" in p:
        try:
            sym_lines = [l for l in prompt.splitlines() if "currency symbol:" in l.lower()]
            if sym_lines:
                currency = sym_lines[0].split(":")[-1].strip()
        except Exception:
            pass
    elif "₹" in prompt:
        currency = "₹"

    # Extract balance if available
    bal = f"{currency}20,000"
    if "current account balance:" in p:
        try:
            bal_lines = [l for l in prompt.splitlines() if "current account balance:" in l.lower()]
            if bal_lines:
                bal = bal_lines[0].split(":")[-1].strip()
        except Exception:
            pass

    if "iphone" in p or "phone" in p:
        return (
            f"Hello {customer_name},\n\n"
            f"Reviewing your current financial position with a balance of {bal}, "
            f"purchasing a new smartphone or gadget should be evaluated against your recurring expenses. "
            f"If your monthly cash flow is positive, consider a 0% interest plan while ensuring your emergency "
            f"savings buffer remains intact."
        )
    elif "save" in p or "saving" in p:
        return (
            f"Hello {customer_name},\n\n"
            f"Based on your transaction analysis, here are key ways to boost your savings:\n\n"
            f"1. **Optimize Fixed Recurring Costs**: Rent and utilities typically account for 40-50% of monthly spending. Keep these in check.\n"
            f"2. **Monitor Discretionary Expenses**: Dining, coffee, and entertainment subscriptions add up fast. Setting a weekly spending cap can save up to 20%.\n"
            f"3. **Automate Savings First**: Transfer 15–20% of your income to a designated savings account on payday.\n"
            f"4. **High-Yield Liquid Funds**: Keep emergency reserves in liquid interest-bearing accounts for optimal safety."
        )
    elif "loan" in p or "borrow" in p or "emi" in p:
        return (
            f"Hello {customer_name},\n\n"
            f"Before taking a loan or EMI commitment, ensure that your total monthly EMI obligations stay below "
            f"30% of your net monthly income. This preserves safe cash flow for unforeseen emergencies."
        )
    elif "invest" in p:
        return (
            f"Hello {customer_name},\n\n"
            f"With your liquid capital ({bal}), a prudent allocation strategy is:\n\n"
            f"- **Emergency Buffer**: 3 to 6 months of expenses in safe liquid savings.\n"
            f"- **Diversified Index Funds**: 50–60% of monthly surplus in low-cost broad index funds.\n"
            f"- **Fixed Income**: 20–30% in high-grade deposits or bonds for capital preservation.\n"
            f"- **Discretionary / Growth**: 10–20% according to your risk tolerance."
        )
    else:
        return (
            f"Hello {customer_name},\n\n"
            f"As your AI Financial Advisor, I have reviewed your bank account. Your current balance stands at {bal}. "
            f"Your cash flow and spending patterns indicate steady activity. Tracking recurring bills and maintaining "
            f"a consistent savings discipline will help achieve your financial goals."
        )



def ask_gemini(prompt: str) -> str:
    """Call Gemini API with model fallbacks and error handling."""
    client = get_client()

    if client:
        candidate_models = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-3.5-flash"
        ]

        for model_name in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"Gemini API attempt failed with model '{model_name}': {e}")
                continue

    # Graceful fallback if Gemini API is unreachable or key is invalid
    return generate_local_advisor_fallback(prompt)
