"""
Data Models and Schemas
"""
from pydantic import BaseModel
from typing import Optional


class MetricsData(BaseModel):
    cpu: float
    memory: float
    disk: float
    risk_score: int
    anomaly: int


class AlertData(BaseModel):
    alert_type: str
    severity: str
    message: str
    metrics: Optional[dict] = None


class LogData(BaseModel):
    timestamp: str
    cpu: float
    memory: float
    disk: float
    risk_score: int
    anomaly: int
