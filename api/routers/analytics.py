from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
        days: int = Query(7, description="Период в днях"),
        db: Session = Depends(get_db)
):
    """Данные для главного дашборда"""
    try:
        stats = AnalyticsService.get_dashboard_metrics(db, days)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-patterns")
async def get_risk_patterns(
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """Топ паттернов риска"""
    try:
        patterns = AnalyticsService.get_top_risk_patterns(db, limit)
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feature-importance")
async def get_feature_importance():
    """Важность признаков ML модели"""
    try:
        from ml.predictor import FraudPredictor
        predictor = FraudPredictor()
        importance = predictor.get_feature_importance()
        return importance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
