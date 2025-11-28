from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text, JSON
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))

    client_id = Column(String, index=True, nullable=True)
    amount = Column(Float, nullable=False)
    destination_id = Column(String, nullable=True)

    os_ver_count_30d = Column(Float)
    phone_model_count_30d = Column(Float)
    logins_7d = Column(Float)
    logins_30d = Column(Float)
    logins_per_day_7 = Column(Float)
    logins_per_day_30 = Column(Float)
    rel_change_7_vs_30 = Column(Float)
    share_7_of_30 = Column(Float)
    mean_interval_30d = Column(Float)
    std_interval_30d = Column(Float)
    var_interval_30d = Column(Float)
    ewm_interval_7d = Column(Float)
    burstiness = Column(Float)
    fano_factor = Column(Float)
    z_score_7d_vs_30d = Column(Float)

    fraud_probability = Column(Float, nullable=True)
    is_fraud = Column(Boolean, nullable=True)
    risk_level = Column(String, nullable=True)
    reasons = Column(JSON, nullable=True)
    model_version = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(String, nullable=True)
    review_status = Column(String, nullable=True)


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, index=True)

    alert_type = Column(String)
    severity = Column(String)
    message = Column(Text)

    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String, nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
