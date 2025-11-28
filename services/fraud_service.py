from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime

from models.database import Transaction as DBTransaction, AlertLog
from api.schemas import TransactionPredictRequest, TransactionPredictResponse, RiskLevel


class FraudService:

    @staticmethod
    def determine_risk_level(fraud_probability: float) -> RiskLevel:
        if fraud_probability >= 0.9:
            return RiskLevel.CRITICAL
        elif fraud_probability >= 0.7:
            return RiskLevel.HIGH
        elif fraud_probability >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    @staticmethod
    def generate_fraud_reasons(features: Dict, probability: float) -> List[str]:
        reasons = []

        if features.get('amount', 0) > 1000000:
            reasons.append(f"Крупная сумма транзакции ({features['amount']:.0f} тг)")
        elif features.get('amount', 0) > 500000:
            reasons.append(f"Повышенная сумма транзакции ({features['amount']:.0f} тг)")

        if features.get('phone_model_count_30d', 0) >= 5:
            reasons.append(f"Множество устройств за 30 дней ({features['phone_model_count_30d']:.0f})")

        if features.get('os_ver_count_30d', 0) >= 5:
            reasons.append(f"Частая смена ОС ({features['os_ver_count_30d']:.0f} версий)")

        if features.get('logins_30d', 0) < 5:
            reasons.append(f"Низкая активность входов ({features.get('logins_30d', 0):.0f} за 30 дней)")

        if features.get('rel_change_7_vs_30', 0) > 3:
            reasons.append("Резкий всплеск активности за последнюю неделю")

        if features.get('burstiness', 0) > 0.8:
            reasons.append("Аномальная нестабильность паттерна входов")

        if abs(features.get('z_score_7d_vs_30d', 0)) > 3:
            reasons.append("Сильное отклонение поведения от нормы")

        if not reasons and probability > 0.7:
            reasons.append("Множественные аномалии в паттернах поведения")

        return reasons

    @staticmethod
    def save_transaction(db: Session, request: TransactionPredictRequest, response: TransactionPredictResponse):
        try:
            transaction = DBTransaction(
                transaction_id=response.transaction_id,
                client_id=request.client_id,
                amount=request.amount,

                os_ver_count_30d=request.os_ver_count_30d,
                phone_model_count_30d=request.phone_model_count_30d,
                logins_7d=request.logins_7d,
                logins_30d=request.logins_30d,
                logins_per_day_7=request.logins_per_day_7,
                logins_per_day_30=request.logins_per_day_30,
                rel_change_7_vs_30=request.rel_change_7_vs_30,
                share_7_of_30=request.share_7_of_30,
                mean_interval_30d=request.mean_interval_30d,
                std_interval_30d=request.std_interval_30d,
                var_interval_30d=request.var_interval_30d,
                ewm_interval_7d=request.ewm_interval_7d,
                burstiness=request.burstiness,
                fano_factor=request.fano_factor,
                z_score_7d_vs_30d=request.z_score_7d_vs_30d,

                fraud_probability=response.fraud_probability,
                is_fraud=response.is_fraud,
                risk_level=response.risk_level.value,
                reasons=response.reasons,
                model_version=response.model_version
            )

            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            if response.is_fraud:
                FraudService.create_alert(db, transaction, response)

        except Exception as e:
            db.rollback()
            print(f"Error saving transaction: {e}")

    @staticmethod
    def save_batch_transactions(db: Session, transactions: List[TransactionPredictRequest],
                                results: List[TransactionPredictResponse]):
        for trans, result in zip(transactions, results):
            FraudService.save_transaction(db, trans, result)

    @staticmethod
    def create_alert(db: Session, transaction: DBTransaction, response: TransactionPredictResponse):
        try:
            severity_map = {
                RiskLevel.LOW: "low",
                RiskLevel.MEDIUM: "medium",
                RiskLevel.HIGH: "high",
                RiskLevel.CRITICAL: "critical"
            }

            alert = AlertLog(
                transaction_id=transaction.transaction_id,
                alert_type="fraud_detected",
                severity=severity_map[response.risk_level],
                message=f"Обнаружена подозрительная транзакция: {', '.join(response.reasons)}"
            )

            db.add(alert)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error creating alert: {e}")