from sqlalchemy.orm import Session

from app.models import (
    Loan,
    Recommendation,
    Account,
)


class PurchaseService:

    def __init__(self, db: Session):
        self.db = db

    def save_recommendation(
        self,
        customer_id,
        recommendation
    ):
        rec = Recommendation(
            customer_id=customer_id,
            merchant_name=recommendation["merchant"],
            recommended_product=recommendation["product"],
            original_price=recommendation["price"],
            discounted_price=recommendation["price"],
            emi_amount=recommendation["emi_monthly"],
            confidence_score=95,
            reason="AI Recommendation"
        )

        self.db.add(rec)
        self.db.flush()

        return rec

    def create_loan(
        self,
        customer_id,
        recommendation
    ):

        loan = Loan(
            customer_id=customer_id,
            principal_amount=recommendation["price"],
            interest_rate=recommendation["interest_rate"],
            tenure_months=12,
            emi=recommendation["emi_monthly"],
            frozen_amount=recommendation["emi_monthly"],
            status="ACTIVE"
        )

        self.db.add(loan)
        self.db.flush()

        return loan

    def update_account(
        self,
        account,
        recommendation
    ):

        account.balance = (
            float(account.balance)
            - recommendation["price"]
        )

        return account
    def execute_purchase(self, customer_id: int, offer: dict, account: Account):
        amount = float(offer["amount"])
        current_balance = float(account.balance)

        if offer["type"] != "loan" and amount > current_balance:
            loan_offer = {
                "type": "loan",
                "title": "Instant Personal Loan Offer",
                "product": "Pre-approved Personal Loan",
                "merchant": "AI Banking Credit Desk",
                "amount": 15000.00,
                "monthly_emi": 1381.25,
                "tenure_months": 12,
                "interest_rate": 10.5,
                "discount_percent": 0,
                "reason": f"Your balance is ${current_balance:,.2f}, so this purchase cannot continue. AI recommends a loan offer instead.",
                "cta": "Accept Loan Offer",
            }

            return {
                "status": "LOAN_RECOMMENDED",
                "message": "Insufficient balance. Loan offer recommended.",
                "balance": current_balance,
                "offer": loan_offer,
            }

        if offer["type"] == "loan":
            account.balance = current_balance + amount
            message = "Loan credited successfully."
        else:
            account.balance = current_balance - amount
            message = "Purchase completed successfully."

        self.db.commit()

        return {
            "status": "SUCCESS",
            "message": message,
            "offer_type": offer["type"],
            "amount": amount,
            "balance": float(account.balance),
            "redirect_url": f"/offers?status=confirmed&type={offer['type']}&amount={amount}&balance={float(account.balance)}",
        }

    def reset_demo_account(self, customer_id: int):
        account = self.db.query(Account).filter(
            Account.customer_id == customer_id
        ).first()

        if not account:
            return {"error": "Account not found"}

        account.balance = 20000.00
        self.db.commit()

        return {
            "status": "RESET",
            "customer_id": customer_id,
            "balance": float(account.balance),
        }
    def execute_purchase(self, customer_id: int, offer: dict, account: Account):
        amount = float(offer["amount"])
        current_balance = float(account.balance)

        if offer["type"] != "loan" and amount > current_balance:
            loan_offer = {
                "type": "loan",
                "title": "Instant Personal Loan Offer",
                "product": "Pre-approved Personal Loan",
                "merchant": "AI Banking Credit Desk",
                "amount": 15000.00,
                "monthly_emi": 1381.25,
                "tenure_months": 12,
                "interest_rate": 10.5,
                "discount_percent": 0,
                "reason": f"Your balance is ${current_balance:,.2f}, so this purchase cannot continue. AI recommends a loan offer instead.",
                "cta": "Accept Loan Offer",
            }

            return {
                "status": "LOAN_RECOMMENDED",
                "message": "Insufficient balance. Loan offer recommended.",
                "balance": current_balance,
                "offer": loan_offer,
            }

        if offer["type"] == "loan":
            account.balance = current_balance + amount
            message = "Loan credited successfully."
        else:
            account.balance = current_balance - amount
            message = "Purchase completed successfully."

        self.db.commit()

        return {
            "status": "SUCCESS",
            "message": message,
            "offer_type": offer["type"],
            "amount": amount,
            "balance": float(account.balance),
            "redirect_url": f"/offers?status=confirmed&type={offer['type']}&amount={amount}&balance={float(account.balance)}",
        }
