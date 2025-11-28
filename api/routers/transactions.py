from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from api.schemas import TransactionResponse, TransactionFilter
from core.database import get_db
from models.database import Transaction as DBTransaction
from services.transaction_service import TransactionService

router = APIRouter()


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
        skip: int = Query(0, ge=0, description="Пропустить N записей"),
        limit: int = Query(100, ge=1, le=1000, description="Лимит записей"),
        is_fraud: Optional[bool] = Query(None, description="Фильтр по мошенничеству"),
        risk_level: Optional[str] = Query(None, description="Фильтр по уровню риска"),
        min_amount: Optional[float] = Query(None, description="Минимальная сумма"),
        max_amount: Optional[float] = Query(None, description="Максимальная сумма"),
        start_date: Optional[datetime] = Query(None, description="Начало периода"),
        end_date: Optional[datetime] = Query(None, description="Конец периода"),
        db: Session = Depends(get_db)
):
    """Получение списка транзакций"""
    try:
        transactions = TransactionService.get_filtered_transactions(
            db=db,
            skip=skip,
            limit=limit,
            is_fraud=is_fraud,
            risk_level=risk_level,
            min_amount=min_amount,
            max_amount=max_amount,
            start_date=start_date,
            end_date=end_date
        )
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
        transaction_id: str,
        db: Session = Depends(get_db)
):
    """Получение детальной информации о транзакции"""
    transaction = db.query(DBTransaction).filter(
        DBTransaction.transaction_id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")

    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(
        transaction_id: str,
        db: Session = Depends(get_db)
):
    """Удаление транзакции"""
    transaction = db.query(DBTransaction).filter(
        DBTransaction.transaction_id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")

    db.delete(transaction)
    db.commit()

    return {"message": "Транзакция удалена", "transaction_id": transaction_id}


@router.get("/stats/summary")
async def get_transactions_summary(
        days: int = Query(7, ge=1, le=365, description="Период в днях"),
        db: Session = Depends(get_db)
):
    """Сводная статистика транзакций"""
    start_date = datetime.utcnow() - timedelta(days=days)

    stats = TransactionService.get_summary_stats(db, start_date)

    return stats