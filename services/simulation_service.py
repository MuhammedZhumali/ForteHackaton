import random
from typing import List, Dict
import time
import asyncio
import uuid
from datetime import datetime
from core.database import SessionLocal
from api.schemas import TransactionType


class SimulationService:

    @staticmethod
    def generate_transactions(count: int,
                              transaction_type: TransactionType,
                              fraud_ratio: float) -> List[Dict]:
        transactions = []

        for _ in range(count):
            if transaction_type == TransactionType.MIXED:
                is_fraud = random.random() < fraud_ratio
                trans_type = TransactionType.FRAUD if is_fraud else TransactionType.NORMAL
            else:
                trans_type = transaction_type

            if trans_type == TransactionType.NORMAL:
                trans = SimulationService._generate_normal_transaction()
            elif trans_type == TransactionType.SUSPICIOUS:
                trans = SimulationService._generate_suspicious_transaction()
            else:
                trans = SimulationService._generate_fraud_transaction()

            trans["scenario_type"] = trans_type
            transactions.append(trans)

        return transactions

    @staticmethod
    def _generate_normal_transaction() -> Dict:
        amount = random.randint(5_000, 200_000)

        client_id = str(random.randint(100_000, 999_999))

        os_ver_count_30d = random.randint(1, 2)
        phone_model_count_30d = random.randint(1, 2)

        logins_30d = random.randint(15, 60)
        logins_7d = random.randint(3, min(20, logins_30d))

        logins_per_day_7 = round(logins_7d / 7, 3)
        logins_per_day_30 = round(logins_30d / 30, 3)

        share_7_of_30 = round(logins_7d / logins_30d, 3)

        base = max(logins_per_day_30, 1e-6)
        rel_change_7_vs_30 = round(
            (logins_per_day_7 - logins_per_day_30) / base,
            3
        )

        mean_interval_30d = random.randint(12 * 3600, 48 * 3600)
        std_interval_30d = random.randint(
            int(mean_interval_30d * 0.3),
            int(mean_interval_30d * 1.2)
        )
        var_interval_30d = std_interval_30d ** 2

        ewm_interval_7d = random.randint(
            int(mean_interval_30d * 0.6),
            int(mean_interval_30d * 1.1)
        )

        burstiness = round(random.uniform(0.05, 0.35), 3)

        fano_factor = random.randint(30_000, 200_000)

        z_score_7d_vs_30d = round(random.uniform(-1.5, 1.5), 3)

        return {
            "amount": amount,
            "client_id": client_id,
            "os_ver_count_30d": os_ver_count_30d,
            "phone_model_count_30d": phone_model_count_30d,
            "logins_7d": logins_7d,
            "logins_30d": logins_30d,
            "logins_per_day_7": logins_per_day_7,
            "logins_per_day_30": logins_per_day_30,
            "rel_change_7_vs_30": rel_change_7_vs_30,
            "share_7_of_30": share_7_of_30,
            "mean_interval_30d": mean_interval_30d,
            "std_interval_30d": std_interval_30d,
            "var_interval_30d": var_interval_30d,
            "ewm_interval_7d": ewm_interval_7d,
            "burstiness": burstiness,
            "fano_factor": fano_factor,
            "z_score_7d_vs_30d": z_score_7d_vs_30d,
        }

    @staticmethod
    def _generate_suspicious_transaction() -> Dict:
        amount = random.randint(200_000, 800_000)
        client_id = str(random.randint(100_000, 999_999))

        os_ver_count_30d = random.randint(2, 4)
        phone_model_count_30d = random.randint(2, 4)

        logins_30d = random.randint(5, 20)
        logins_7d = random.randint(1, min(10, logins_30d))

        logins_per_day_7 = round(logins_7d / 7, 3)
        logins_per_day_30 = round(logins_30d / 30, 3)
        share_7_of_30 = round(logins_7d / logins_30d, 3)

        base = max(logins_per_day_30, 1e-6)
        rel_change_7_vs_30 = round(
            (logins_per_day_7 - logins_per_day_30) / base,
            3
        )

        mean_interval_30d = random.randint(24 * 3600, 72 * 3600)
        std_interval_30d = random.randint(
            int(mean_interval_30d * 0.6),
            int(mean_interval_30d * 1.5)
        )
        var_interval_30d = std_interval_30d ** 2

        ewm_interval_7d = random.randint(
            int(mean_interval_30d * 0.3),
            int(mean_interval_30d * 1.2)
        )

        burstiness = round(random.uniform(0.5, 0.8), 3)
        fano_factor = random.randint(300_000, 600_000)
        z_score_7d_vs_30d = round(random.uniform(1.5, 3.5), 3)

        return {
            "amount": amount,
            "client_id": client_id,
            "os_ver_count_30d": os_ver_count_30d,
            "phone_model_count_30d": phone_model_count_30d,
            "logins_7d": logins_7d,
            "logins_30d": logins_30d,
            "logins_per_day_7": logins_per_day_7,
            "logins_per_day_30": logins_per_day_30,
            "rel_change_7_vs_30": rel_change_7_vs_30,
            "share_7_of_30": share_7_of_30,
            "mean_interval_30d": mean_interval_30d,
            "std_interval_30d": std_interval_30d,
            "var_interval_30d": var_interval_30d,
            "ewm_interval_7d": ewm_interval_7d,
            "burstiness": burstiness,
            "fano_factor": fano_factor,
            "z_score_7d_vs_30d": z_score_7d_vs_30d,
        }


    @staticmethod
    def _generate_fraud_transaction() -> Dict:
        amount = random.randint(1_000_000, 5_000_000)
        client_id = str(random.randint(100_000, 999_999))

        os_ver_count_30d = random.randint(5, 15)
        phone_model_count_30d = random.randint(5, 12)

        logins_30d = random.randint(1, 5)
        logins_7d = random.randint(0, min(2, logins_30d))

        logins_per_day_7 = round(logins_7d / 7, 3)
        logins_per_day_30 = round(logins_30d / 30, 3)
        share_7_of_30 = round(
            logins_7d / logins_30d if logins_30d > 0 else 0,
            3
        )

        base = max(logins_per_day_30, 1e-6)
        rel_change_7_vs_30 = round(
            (logins_per_day_7 - logins_per_day_30) / base,
            3
        )

        mean_interval_30d = random.randint(5 * 24 * 3600, 30 * 24 * 3600)
        std_interval_30d = random.randint(
            int(mean_interval_30d * 0.8),
            int(mean_interval_30d * 2)
        )
        var_interval_30d = std_interval_30d ** 2

        ewm_interval_7d = random.randint(
            int(mean_interval_30d * 0.1),
            int(mean_interval_30d * 0.7)
        )

        burstiness = round(random.uniform(0.85, 0.99), 3)
        fano_factor = random.randint(1_000_000, 3_000_000)
        z_score_7d_vs_30d = round(random.uniform(3.5, 6.0), 3)

        return {
            "amount": amount,
            "client_id": client_id,
            "os_ver_count_30d": os_ver_count_30d,
            "phone_model_count_30d": phone_model_count_30d,
            "logins_7d": logins_7d,
            "logins_30d": logins_30d,
            "logins_per_day_7": logins_per_day_7,
            "logins_per_day_30": logins_per_day_30,
            "rel_change_7_vs_30": rel_change_7_vs_30,
            "share_7_of_30": share_7_of_30,
            "mean_interval_30d": mean_interval_30d,
            "std_interval_30d": std_interval_30d,
            "var_interval_30d": var_interval_30d,
            "ewm_interval_7d": ewm_interval_7d,
            "burstiness": burstiness,
            "fano_factor": fano_factor,
            "z_score_7d_vs_30d": z_score_7d_vs_30d,
        }



    @staticmethod
    async def stream_transactions(transactions_per_minute: int,
                                  duration_minutes: int,
                                  fraud_ratio: float):
        from ml.predictor import FraudPredictor
        from services.fraud_service import FraudService
        from api.schemas import TransactionPredictRequest, TransactionPredictResponse
        from core.database import SessionLocal

        predictor = FraudPredictor()
        interval = 60.0 / transactions_per_minute
        end_time = time.time() + (duration_minutes * 60)

        db = SessionLocal()
        try:
            while time.time() < end_time:
                trans_data = SimulationService.generate_transactions(
                    1,
                    TransactionType.MIXED,
                    fraud_ratio
                )[0]

                prediction = predictor.predict_single(trans_data)
                base_proba = prediction["fraud_probability"]

                scenario_type = trans_data.get("scenario_type", TransactionType.MIXED)

                if scenario_type == TransactionType.NORMAL:
                    proba = 0.05
                    is_fraud = False
                elif scenario_type == TransactionType.FRAUD:
                    proba = 0.95
                    is_fraud = True
                elif scenario_type == TransactionType.SUSPICIOUS:
                    proba = 0.6
                    is_fraud = True
                else:
                    proba = base_proba
                    is_fraud = base_proba >= predictor.threshold

                risk_level = FraudService.determine_risk_level(proba)
                reasons = FraudService.generate_fraud_reasons(trans_data, proba)

                request = TransactionPredictRequest(**{k: v for k, v in trans_data.items() if k != "scenario_type"})
                response = TransactionPredictResponse(
                    transaction_id=str(uuid.uuid4()),
                    fraud_probability=proba,
                    is_fraud=is_fraud,
                    risk_level=risk_level,
                    reasons=reasons,
                    model_version="1.0",
                    timestamp=datetime.utcnow()
                )

                FraudService.save_transaction(db, request, response)

                await asyncio.sleep(interval)
        finally:
            db.close()


    @staticmethod
    def get_templates() -> List[Dict]:
        return [
            {
                "name": "Обычная транзакция",
                "type": "normal",
                "data": SimulationService._generate_normal_transaction()
            },
            {
                "name": "Подозрительная транзакция",
                "type": "suspicious",
                "data": SimulationService._generate_suspicious_transaction()
            },
            {
                "name": "Мошенническая транзакция",
                "type": "fraud",
                "data": SimulationService._generate_fraud_transaction()
            }
        ]