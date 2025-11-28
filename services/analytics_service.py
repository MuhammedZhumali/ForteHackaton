from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict

from models.database import Transaction as DBTransaction


class AnalyticsService:
    @staticmethod
    def get_dashboard_metrics(db: Session, days: int) -> Dict:
        start_date = datetime.utcnow() - timedelta(days=days)

        total = db.query(func.count(DBTransaction.id)).filter(
            DBTransaction.created_at >= start_date
        ).scalar() or 0

        fraud_count = db.query(func.count(DBTransaction.id)).filter(
            DBTransaction.created_at >= start_date,
            DBTransaction.is_fraud == True
        ).scalar() or 0

        avg_fraud_amount = db.query(func.avg(DBTransaction.amount)).filter(
            DBTransaction.created_at >= start_date,
            DBTransaction.is_fraud == True
        ).scalar() or 0

        patterns = AnalyticsService.get_top_risk_patterns(db, 5)

        return {
            "total_transactions": total,
            "fraud_detected": fraud_count,
            "fraud_rate": (fraud_count / total) if total else 0,
            "avg_fraud_amount": float(avg_fraud_amount),
            "period_days": days,
            "top_risk_patterns": patterns
        }

    @staticmethod
    def get_top_risk_patterns(db: Session, limit: int) -> List[Dict]:
        fraud_transactions = db.query(DBTransaction).filter(
            DBTransaction.is_fraud == True
        ).limit(100).all()

        if not fraud_transactions:
            return []

        patterns = []

        avg_amount = sum(t.amount for t in fraud_transactions) / len(fraud_transactions)
        avg_devices = sum(t.phone_model_count_30d or 0 for t in fraud_transactions) / len(fraud_transactions)
        avg_logins = sum(t.logins_30d or 0 for t in fraud_transactions) / len(fraud_transactions)

        patterns.append({
            "pattern": "Высокие суммы",
            "description": f"Средняя сумма мошеннических транзакций: {avg_amount:.0f} тг",
            "prevalence": 0.8
        })

        if avg_devices > 3:
            patterns.append({
                "pattern": "Множество устройств",
                "description": f"В среднем {avg_devices:.1f} устройств за 30 дней",
                "prevalence": 0.7
            })

        if avg_logins < 10:
            patterns.append({
                "pattern": "Низкая активность",
                "description": f"В среднем {avg_logins:.1f} входов за 30 дней",
                "prevalence": 0.6
            })

        return patterns[:limit]
