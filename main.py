from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from fastapi.staticfiles import StaticFiles
import os
from api.routers import transactions, fraud_detection, analytics, simulation
from core.config import settings
from core.database import engine, Base
from ml.model_loader import ModelLoader


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Загрузка ML моделей.")
    try:
        ModelLoader.load_models()
        print("Модели успешно загружены!")
    except Exception as e:
        print(f"Ошибка загрузки моделей: {e}")

    print("Инициализация базы данных.")
    Base.metadata.create_all(bind=engine)
    print("База данных готова!")

    yield

    print("Завершение работы.")


app = FastAPI(
    title="Forte Fraud Shield API",
    description="""
    Система детекции мошеннических транзакций для ForteBank
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    fraud_detection.router,
    prefix="/api/v1/fraud",
    tags=["fraud-detection"]
)

app.include_router(
    transactions.router,
    prefix="/api/v1/transactions",
    tags=["transactions"]
)

app.mount(
    "/webapp",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "webapp"), html=True),
    name="webapp",
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["analytics"]
)

app.include_router(
    simulation.router,
    prefix="/api/v1/simulation",
    tags=["simulation"]
)

@app.get("/", tags=["health"])
async def root():
    return {
        "service": "Forte Fraud Shield API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["health"])
async def health_check():
    health_status = {
        "status": "healthy",
        "components": {
            "api": "ok",
            "ml_models": "checking",
            "database": "checking"
        }
    }

    try:
        if ModelLoader.models:
            health_status["components"]["ml_models"] = "ok"
            health_status["components"]["models_loaded"] = len(ModelLoader.models)
        else:
            health_status["components"]["ml_models"] = "not_loaded"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["ml_models"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    try:
        from sqlalchemy import text
        from core.database import SessionLocal

        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["components"]["database"] = "ok"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    return health_status


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )