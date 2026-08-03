def calculate_financial_health(customer, account, transactions):

    annual_salary = float(customer.salary)
    monthly_salary = float(account.monthly_salary)

    savings = float(account.savings)

    total_spent = sum(
        float(t.amount)
        for t in transactions
        if t.transaction_type.lower() == "debit"
    )

    score = 0

    # Savings Ratio (40)
    savings_ratio = (savings / annual_salary) * 100

    if savings_ratio >= 50:
        score += 40
    elif savings_ratio >= 30:
        score += 30
    elif savings_ratio >= 20:
        score += 20
    else:
        score += 10

    # Monthly Spending (25)
    if total_spent <= monthly_salary * 0.60:
        score += 25
    elif total_spent <= monthly_salary * 0.80:
        score += 15
    else:
        score += 5

    # Salary Stability (20)
    if annual_salary >= 90000:
        score += 20
    elif annual_salary >= 60000:
        score += 15
    else:
        score += 10

    # Account Age (15)
    score += 15

    if score >= 90:
        status = "Excellent"
    elif score >= 75:
        status = "Good"
    elif score >= 60:
        status = "Average"
    else:
        status = "Needs Attention"
    advice = []

    if savings_ratio >= 50:
        advice.append("Excellent emergency fund maintained.")
    elif savings_ratio >= 30:
        advice.append("Savings are healthy.")
    else:
        advice.append("Increase your monthly savings.")

    spending_ratio = (total_spent / monthly_salary) * 100

    if spending_ratio > 80:
        advice.append("Monthly spending is very high. Reduce discretionary expenses.")
    elif spending_ratio > 60:
        advice.append("Monitor your monthly spending carefully.")
    else:
        advice.append("Spending is well under control.")

    if annual_salary >= 90000:
        advice.append("Income level supports long-term investments.")
    else:
        advice.append("Focus on increasing income and savings.")

    if score >= 90:
        advice.append("Overall financial health is excellent.")
    elif score >= 75:
        advice.append("Financial health is good with room for improvement.")
    else:
        advice.append("Consider reducing expenses and improving savings.")
    return {
    "financial_health_score": score,
    "status": status,
    "annual_salary": annual_salary,
    "monthly_salary": monthly_salary,
    "total_spent": round(total_spent, 2),
    "total_savings": savings,
    "savings_ratio": round(savings_ratio, 2),
    "spending_ratio": round(spending_ratio, 2),
    "advice": advice,
}
