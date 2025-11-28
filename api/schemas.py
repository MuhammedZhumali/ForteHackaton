from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TransactionType(str, Enum):
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    FRAUD = "fraud"
    MIXED = "mixed"

class TransactionPredictRequest(BaseModel):

    amount: float = Field(..., description="Сумма транзакции", ge=0)
    client_id: Optional[str] = Field(None, description="ID клиента")

    os_ver_count_30d: float = Field(..., description="Количество версий ОС за 30 дней")
    phone_model_count_30d: float = Field(..., description="Количество моделей телефона за 30 дней")
    logins_7d: float = Field(..., description="Количество логинов за 7 дней")
    logins_30d: float = Field(..., description="Количество логинов за 30 дней")
    logins_per_day_7: float = Field(..., description="Логины в день за 7 дней")
    logins_per_day_30: float = Field(..., description="Логины в день за 30 дней")

    rel_change_7_vs_30: float = Field(..., description="Относительное изменение частоты логинов")
    share_7_of_30: float = Field(..., description="Доля логинов 7д от 30д")
    mean_interval_30d: float = Field(..., description="Средний интервал между сессиями (сек)")
    std_interval_30d: float = Field(..., description="Стандартное отклонение интервалов")
    var_interval_30d: float = Field(..., description="Дисперсия интервалов")
    ewm_interval_7d: float = Field(..., description="Экспоненциально взвешенное среднее")

    burstiness: float = Field(..., description="Показатель взрывности логинов")
    fano_factor: float = Field(..., description="Fano-фактор интервалов")
    z_score_7d_vs_30d: float = Field(..., description="Z-скор среднего интервала")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 1500000,
                "client_id": "12345",
                "os_ver_count_30d": 5,
                "phone_model_count_30d": 5,
                "logins_7d": 1,
                "logins_30d": 2,
                "logins_per_day_7": 0.14,
                "logins_per_day_30": 0.067,
                "rel_change_7_vs_30": 2.0,
                "share_7_of_30": 0.5,
                "mean_interval_30d": 200000,
                "std_interval_30d": 400000,
                "var_interval_30d": 160000000000,
                "ewm_interval_7d": 10000,
                "burstiness": 0.9,
                "fano_factor": 500000,
                "z_score_7d_vs_30d": 3.0
            }
        }


class TransactionPredictResponse(BaseModel):
    transaction_id: str
    fraud_probability: float = Field(..., ge=0, le=1)
    is_fraud: bool
    risk_level: RiskLevel
    reasons: List[str] = Field(default_factory=list)
    model_version: str = "1.0"
    timestamp: datetime


    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
                "fraud_probability": 0.9443,
                "is_fraud": True,
                "risk_level": "CRITICAL",
                "reasons": [
                    "Крупная сумма транзакции (1500000 тг)",
                    "Множество устройств за 30 дней (5)",
                    "Низкая активность входов (2 за 30 дней)"
                ],
                "model_version": "GradientBoosting_v1.0",
                "timestamp": "2025-11-28T10:00:00Z"
            }
        }


class BatchPredictRequest(BaseModel):
    transactions: List[TransactionPredictRequest] = Field(..., max_length=1000)


class BatchPredictResponse(BaseModel):
    results: List[TransactionPredictResponse]
    total_transactions: int
    fraud_detected: int
    fraud_rate: float
    processed_at: datetime

class SimulateTransactionRequest(BaseModel):
    count: int = Field(10, ge=1, le=500, description="Количество транзакций")
    transaction_type: TransactionType = Field(TransactionType.MIXED, description="Тип транзакций")
    fraud_ratio: float = Field(0.15, ge=0, le=1, description="Доля мошенничества для mixed")

    class Config:
        json_schema_extra = {
            "example": {
                "count": 100,
                "transaction_type": "mixed",
                "fraud_ratio": 0.15
            }
        }


class GeneratedTransaction(TransactionPredictRequest):
    fraud_probability: float
    is_fraud: bool
    predicted_at: datetime
    scenario_type: TransactionType


class SimulateTransactionResponse(BaseModel):
    transactions: List[GeneratedTransaction]
    total_generated: int
    fraud_detected: int
    fraud_rate: float
    generated_at: datetime


class StreamTransactionsRequest(BaseModel):
    transactions_per_minute: int = Field(10, ge=1, le=100)
    duration_minutes: int = Field(5, ge=1, le=60)
    fraud_ratio: float = Field(0.1, ge=0, le=1)
    transaction_type: TransactionType = Field(
        TransactionType.MIXED,
        description="Тип транзакций в потоке"
    )


class TransactionResponse(BaseModel):
    transaction_id: str
    client_id: Optional[str]
    amount: float
    fraud_probability: Optional[float]
    is_fraud: Optional[bool]
    risk_level: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionFilter(BaseModel):
    is_fraud: Optional[bool] = None
    risk_level: Optional[RiskLevel] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
