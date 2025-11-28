from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio

from api.schemas import (
    SimulateTransactionRequest,
    SimulateTransactionResponse,
    StreamTransactionsRequest,
    GeneratedTransaction,
    TransactionType,
)
from core.database import get_db
from services.simulation_service import SimulationService

router = APIRouter()


@router.post("/generate", response_model=SimulateTransactionResponse)
async def generate_transactions(
        request: SimulateTransactionRequest,
        db: Session = Depends(get_db)
):
    """Генерация тестовых транзакций"""
    if request.count > 500:
        raise HTTPException(status_code=400, detail="Максимум 500 транзакций за раз")

    try:
        transactions = SimulationService.generate_transactions(
            count=request.count,
            transaction_type=request.transaction_type,
            fraud_ratio=request.fraud_ratio
        )

        from ml.predictor import FraudPredictor
        predictor = FraudPredictor()

        results = []
        for trans in transactions:
            prediction = predictor.predict_single(trans)
            base_proba = prediction["fraud_probability"]

            scenario_type = trans.get("scenario_type", TransactionType.MIXED)

            proba = base_proba
            is_fraud = proba >= predictor.threshold

            result = GeneratedTransaction(
                **{k: v for k, v in trans.items() if k != "scenario_type"},
                fraud_probability=proba,
                is_fraud=is_fraud,
                predicted_at=datetime.utcnow(),
                scenario_type=scenario_type
            )

            results.append(result)

        fraud_detected = sum(1 for r in results if r.is_fraud)

        response = SimulateTransactionResponse(
            transactions=results,
            total_generated=len(results),
            fraud_detected=fraud_detected,
            fraud_rate=fraud_detected / len(results) if results else 0,
            generated_at=datetime.utcnow()
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")



@router.post("/stream")
async def start_transaction_stream(
        request: StreamTransactionsRequest,
        background_tasks: BackgroundTasks
):
    """Запуск потока транзакций в реальном времени"""
    if request.transactions_per_minute > 100:
        raise HTTPException(status_code=400, detail="Максимум 100 транзакций в минуту")

    if request.duration_minutes > 60:
        raise HTTPException(status_code=400, detail="Максимум 60 минут")

    total_transactions = request.transactions_per_minute * request.duration_minutes

    asyncio.create_task(
        SimulationService.stream_transactions(
            transactions_per_minute=request.transactions_per_minute,
            duration_minutes=request.duration_minutes,
            fraud_ratio=request.fraud_ratio,
        )
    )

    return {
        "status": "started",
        "message": "Поток транзакций запущен",
        "config": {
            "transactions_per_minute": request.transactions_per_minute,
            "duration_minutes": request.duration_minutes,
            "total_expected": total_transactions,
            "fraud_ratio": request.fraud_ratio
        },
        "started_at": datetime.utcnow()

    }


@router.get("/templates")
async def get_transaction_templates():
    """Шаблоны транзакций"""
    templates = SimulationService.get_templates()
    return {
        "templates": templates,
        "total": len(templates)
    }
