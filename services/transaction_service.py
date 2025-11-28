from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from models.database import Transaction as DBTransaction


class TransactionService:
    @staticmethod
    def get_filtered_transactions(
            db: Session,
            skip: int = 0,
            limit: int = 100,
            is_fraud: Optional[bool] = None,
            risk_level: Optional[str] = None,
            min_amount: Optional[float] = None,
            max_amount: Optional[float] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
    ) -> List[DBTransaction]:

        query = db.query(DBTransaction)

        if is_fraud is not None:
            query = query.filter(DBTransaction.is_fraud == is_fraud)

        if risk_level:
            query = query.filter(DBTransaction.risk_level == risk_level)

        if min_amount is not None:
            query = query.filter(DBTransaction.amount >= min_amount)

        if max_amount is not None:
            query = query.filter(DBTransaction.amount <= max_amount)

        if start_date:
            query = query.filter(DBTransaction.created_at >= start_date)

        if end_date:
            query = query.filter(DBTransaction.created_at <= end_date)

        query = query.order_by(DBTransaction.created_at.desc())

        transactions = query.offset(skip).limit(limit).all()

        return transactions

    @staticmethod
    def get_summary_stats(db: Session, start_date: datetime) -> dict:
        from sqlalchemy import func

        total = db.query(func.count(DBTransaction.id)).filter(
            DBTransaction.created_at >= start_date
        ).scalar()

        fraud_count = db.query(func.count(DBTransaction.id)).filter(
            DBTransaction.created_at >= start_date,
            DBTransaction.is_fraud == True
        ).scalar()

        avg_fraud_amount = db.query(func.avg(DBTransaction.amount)).filter(
            DBTransaction.created_at >= start_date,
            DBTransaction.is_fraud == True
        ).scalar()

        risk_levels = db.query(
            DBTransaction.risk_level,
            func.count(DBTransaction.id)
        ).filter(
            DBTransaction.created_at >= start_date
        ).group_by(DBTransaction.risk_level).all()

        risk_distribution = {level: count for level, count in risk_levels if level}

        return {
            "total_transactions": total or 0,
            "fraud_detected": fraud_count or 0,
            "fraud_rate": (fraud_count / total) if total else 0,
            "avg_fraud_amount": float(avg_fraud_amount) if avg_fraud_amount else 0,
            "risk_distribution": risk_distribution,
            "period_start": start_date.isoformat(),
            "period_end": datetime.utcnow().isoformat()
        }