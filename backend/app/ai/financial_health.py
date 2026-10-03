def calculate_financial_health(customer, account, transactions):
    balance = float(account.balance) if account and account.balance else 0.0
    savings = float(account.savings) if account and account.savings else 0.0

    annual_salary = float(customer.salary) if customer and customer.salary else 0.0
    monthly_salary = (
        float(account.monthly_salary)
        if account and account.monthly_salary
        else (annual_salary / 12.0 if annual_salary > 0 else 0.0)
    )

    if annual_salary == 0.0 and monthly_salary > 0.0:
        annual_salary = monthly_salary

    total_spent = sum(
        float(t.amount)
        for t in transactions
        if t.transaction_type and t.transaction_type.lower() == "debit"
    )

    # Compute statement span in months so monthly spending ratio is accurate
    num_months = 1
    dates_found = [t.transaction_date for t in transactions if getattr(t, "transaction_date", None)]
    if dates_found:
        try:
            span_days = max(1, (max(dates_found) - min(dates_found)).days)
            num_months = max(1, round(span_days / 30.0))
        except Exception:
            num_months = 1

    monthly_spent = round(total_spent / num_months, 2) if total_spent > 0 else 0.0

    # CRITICAL RULE: If both Total Balance <= 0 and Savings <= 0, Financial Health MUST be "Poor"
    if balance <= 0.0 and savings <= 0.0:
        spending_ratio = round((monthly_spent / monthly_salary) * 100, 2) if monthly_salary > 0 else 0.0
        has_activity = total_spent > 0 or monthly_salary > 0 or len(transactions) > 0
        poor_score = 20 if has_activity else 0
        advice = [
            "Critical Alert: Total account balance and savings are both zero.",
            "Immediate action required: Deposit funds or reduce expenses to restore positive liquidity.",
            "Build an emergency savings buffer of at least 20% of your monthly income.",
            "Avoid non-essential spending until your account balance recovers.",
        ]
        return {
            "financial_health_score": poor_score,
            "status": "Poor",
            "annual_salary": round(annual_salary, 2),
            "monthly_salary": round(monthly_salary, 2),
            "total_spent": round(total_spent, 2),
            "monthly_spent": monthly_spent,
            "total_savings": round(savings, 2),
            "savings_ratio": 0.0,
            "spending_ratio": spending_ratio,
            "advice": advice,
        }

    score = 0

    # 1. Savings Ratio (up to 40 pts)
    ref_income = monthly_salary if monthly_salary > 0 else (annual_salary if annual_salary > 0 else balance)
    if ref_income > 0:
        savings_ratio = (savings / ref_income) * 100.0
    elif savings > 0:
        savings_ratio = 35.0
    else:
        savings_ratio = 0.0

    if savings_ratio >= 50:
        score += 40
    elif savings_ratio >= 30:
        score += 30
    elif savings_ratio >= 15:
        score += 20
    elif savings_ratio > 0:
        score += 10
    else:
        score += 0

    # 2. Monthly Spending to Income Ratio (up to 25 pts)
    if monthly_salary > 0:
        spending_ratio = (monthly_spent / monthly_salary) * 100.0
        if spending_ratio <= 60:
            score += 25
        elif spending_ratio <= 80:
            score += 20
        elif spending_ratio <= 95:
            score += 15
        elif spending_ratio <= 105:
            score += 10
        else:
            score += 5
    else:
        spending_ratio = 0.0
        score += 10

    # 3. Liquidity & Balance Health (up to 20 pts)
    if balance > 0 and monthly_spent > 0:
        if balance >= monthly_spent * 1.2:
            score += 20
        elif balance >= monthly_spent * 0.5:
            score += 15
        else:
            score += 10
    elif balance > 0:
        score += 15

    # 4. Cash Flow & Account Stability (up to 15 pts)
    if monthly_salary > 0 and balance > 0:
        score += 15
    elif balance > 0:
        score += 10

    if score >= 85:
        status = "Excellent"
    elif score >= 70:
        status = "Good"
    elif score >= 50:
        status = "Average"
    else:
        status = "Poor"

    advice = []

    if savings_ratio >= 50:
        advice.append(f"Strong emergency buffer maintained ({savings_ratio:.1f}% savings ratio).")
    elif savings_ratio >= 25:
        advice.append(f"Healthy savings reserve ({savings_ratio:.1f}% of monthly inflow).")
    elif savings > 0:
        advice.append("Increase your monthly savings allocation toward a 30% buffer.")
    else:
        advice.append("Zero savings recorded — start setting aside at least 15-20% of income.")

    if monthly_salary > 0:
        if spending_ratio > 95:
            advice.append(f"Monthly expenses ({spending_ratio:.1f}% of income) are high. Cut down top discretionary categories.")
        elif spending_ratio > 70:
            advice.append(f"Monthly spending is moderate ({spending_ratio:.1f}% of income). Monitor variable expenses.")
        else:
            advice.append(f"Monthly spending ({spending_ratio:.1f}% of income) is well under control.")
    else:
        advice.append("Track your monthly income and expenses consistently.")

    if balance >= monthly_spent and monthly_spent > 0:
        advice.append("Closing balance comfortably covers your monthly expense commitments.")
    else:
        advice.append("Focus on growing your closing balance above 1–2 months of expenses.")

    if status in ("Excellent", "Good"):
        advice.append("Overall financial health is strong based on your statement analysis.")
    elif status == "Average":
        advice.append("Financial health is average — reducing expenses will boost your score.")
    else:
        advice.append("Financial health is poor — prioritize rebuilding liquidity and savings.")

    return {
        "financial_health_score": score,
        "status": status,
        "annual_salary": round(annual_salary, 2),
        "monthly_salary": round(monthly_salary, 2),
        "total_spent": round(total_spent, 2),
        "monthly_spent": monthly_spent,
        "total_savings": round(savings, 2),
        "savings_ratio": round(savings_ratio, 2),
        "spending_ratio": round(spending_ratio, 2),
        "advice": advice,
    }
