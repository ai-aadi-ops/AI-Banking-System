def generate_recommendation(
    spending,
    health,
    account,
    card
):

    recommendations = []

    category = spending["highest_spending_category"].lower()

    if category == "shopping":
        recommendations.append({
            "title": "Premium Cashback Credit Card",
            "reason": "High shopping expenses detected.",
            "estimated_savings": "$480/year",
            "confidence": "92%"
        })

    elif category == "fuel":
        recommendations.append({
            "title": "Fuel Rewards Card",
            "reason": "Fuel expenses are higher than average.",
            "estimated_savings": "$220/year",
            "confidence": "90%"
        })

    elif category == "housing":
        recommendations.append({
            "title": "Home Loan Balance Transfer",
            "reason": "Housing is your biggest monthly expense.",
            "estimated_savings": "$900/year",
            "confidence": "94%"
        })

    if health["savings_ratio"] < 30:
        recommendations.append({
            "title": "Monthly SIP Plan",
            "reason": "Savings ratio is below recommended level.",
            "estimated_savings": "$350/month",
            "confidence": "88%"
        })

    if health["spending_ratio"] > 80:
        recommendations.append({
            "title": "Expense Reduction Plan",
            "reason": "Monthly spending is too high.",
            "estimated_savings": "$600/month",
            "confidence": "95%"
        })

    if health["annual_salary"] >= 90000:
        recommendations.append({
            "title": "Wealth Management Portfolio",
            "reason": "Income supports long-term investments.",
            "estimated_savings": "Higher investment returns",
            "confidence": "90%"
        })

    return recommendations
