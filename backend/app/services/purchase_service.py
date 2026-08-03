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

    def execute_purchase(
        self,
        customer_id: int,
        recommendation: dict,
        decision: dict,
        account: Account,
    ):

        if decision["decision"] != "APPROVED":
            return {
                "status": "DECLINED"
            }

        self.save_recommendation(
            customer_id,
            recommendation
        )

        self.create_loan(
            customer_id,
            recommendation
        )

        self.update_account(
            account,
            recommendation
        )

        self.db.commit()

        return {
            "status": "SUCCESS",
            "message": "Purchase completed successfully"
        }
