from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from api.schemas import (
    TransactionPredictRequest,
    TransactionPredictResponse,
    BatchPredictRequest,
    BatchPredictResponse,
    RiskLevel
)
from core.database import get_db
from ml.predictor import FraudPredictor
from services.fraud_service import FraudService

router = APIRouter()


@router.post("/predict", response_model=TransactionPredictResponse)
async def predict_fraud(
        request: TransactionPredictRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    """Индикатор мошенничества для одной транзакции"""
    try:
        predictor = FraudPredictor()
        prediction = predictor.predict_single(request.dict())
        risk_level = FraudService.determine_risk_level(prediction['fraud_probability'])

        reasons = FraudService.generate_fraud_reasons(request.dict(), prediction['fraud_probability'])

        response = TransactionPredictResponse(
            transaction_id=str(uuid.uuid4()),
            fraud_probability=prediction['fraud_probability'],
            is_fraud=prediction['is_fraud'],
            risk_level=risk_level,
            reasons=reasons,
            model_version=prediction.get('model_version', '1.0'),
            timestamp=datetime.utcnow()
        )

        background_tasks.add_task(
            FraudService.save_transaction,
            db=db,
            request=request,
            response=response
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка предсказания: {str(e)}")


@router.post("/batch", response_model=BatchPredictResponse)
async def batch_predict(
        request: BatchPredictRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    """Массовая детекция мошенничества"""
    if len(request.transactions) > 1000:
        raise HTTPException(status_code=400, detail="Максимум 1000 транзакций за раз")

    try:
        predictor = FraudPredictor()
        results = []

        for trans in request.transactions:
            prediction = predictor.predict_single(trans.dict())
            risk_level = FraudService.determine_risk_level(prediction['fraud_probability'])
            reasons = FraudService.generate_fraud_reasons(trans.dict(), prediction['fraud_probability'])

            result = TransactionPredictResponse(
                transaction_id=str(uuid.uuid4()),
                fraud_probability=prediction['fraud_probability'],
                is_fraud=prediction['is_fraud'],
                risk_level=risk_level,
                reasons=reasons,
                model_version=prediction.get('model_version', '1.0'),
                timestamp=datetime.utcnow()
            )
            results.append(result)

        total = len(results)
        fraud_count = sum(1 for r in results if r.is_fraud)

        response = BatchPredictResponse(
            results=results,
            total_transactions=total,
            fraud_detected=fraud_count,
            fraud_rate=fraud_count / total if total > 0 else 0,
            processed_at=datetime.utcnow()
        )

        background_tasks.add_task(
            FraudService.save_batch_transactions,
            db=db,
            transactions=request.transactions,
            results=results
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка пакетного предсказания: {str(e)}")
