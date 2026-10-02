def calculate_financial_health(customer, account, transactions):

    annual_salary = float(customer.salary) if customer and customer.salary else 0.0
    monthly_salary = float(account.monthly_salary) if account and account.monthly_salary else (annual_salary / 12.0 if annual_salary > 0 else 0.0)

    if annual_salary == 0.0 and monthly_salary > 0.0:
        annual_salary = monthly_salary * 12.0

    savings = float(account.savings) if account and account.savings else 0.0

    total_spent = sum(
        float(t.amount)
        for t in transactions
        if t.transaction_type.lower() == "debit"
    )

    score = 0

    # Savings Ratio (40)
    if annual_salary > 0:
        savings_ratio = (savings / annual_salary) * 100
    elif savings > 0:
        savings_ratio = 35.0
    else:
        savings_ratio = 10.0

    if savings_ratio >= 50:
        score += 40
    elif savings_ratio >= 30:
        score += 30
    elif savings_ratio >= 20:
        score += 20
    else:
        score += 10

    # Monthly Spending (25)
    if monthly_salary > 0:
        spending_ratio = (total_spent / monthly_salary) * 100
        if total_spent <= monthly_salary * 0.60:
            score += 25
        elif total_spent <= monthly_salary * 0.80:
            score += 15
        else:
            score += 5
    else:
        spending_ratio = 50.0
        score += 20

    # Salary Stability (20)
    if annual_salary > 0:
        score += 20
    else:
        score += 15

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

    if monthly_salary > 0:
        spending_ratio = (total_spent / monthly_salary) * 100
        if spending_ratio > 80:
            advice.append("Monthly spending is very high. Reduce discretionary expenses.")
        elif spending_ratio > 60:
            advice.append("Monitor your monthly spending carefully.")
        else:
            advice.append("Spending is well under control.")
    else:
        spending_ratio = 0.0
        advice.append("Track your monthly expenses to build a consistent budget.")

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
