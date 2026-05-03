"""
FastAPI SOC Backend Server
Enterprise Security Operations Center - Main API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from datetime import datetime

from .collector import get_metrics, get_process_info
from .ai_engine import AIEngine
from .database import (
    init_database,
    insert_log,
    insert_alert,
    get_recent_logs,
    get_recent_alerts,
    get_statistics
)
from .models import MetricsData, AlertData

# Initialize FastAPI app
app = FastAPI(
    title="WiFi SOC v7",
    description="Enterprise AI-powered Security Operations Center",
    version="7.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
ai_engine = AIEngine()
init_database()

# Global state
risk_history = []
anomaly_count = 0


def calculate_risk_score(metrics):
    """
    Calculate risk score based on system metrics
    Scale: 0-100
    """
    risk = 25  # Base risk
    
    # CPU risk
    if metrics['cpu'] > 90:
        risk += 30
    elif metrics['cpu'] > 75:
        risk += 20
    elif metrics['cpu'] > 50:
        risk += 10
    
    # Memory risk
    if metrics['memory'] > 90:
        risk += 25
    elif metrics['memory'] > 75:
        risk += 15
    elif metrics['memory'] > 60:
        risk += 8
    
    # Disk risk
    if metrics['disk'] > 90:
        risk += 20
    elif metrics['disk'] > 80:
        risk += 10
    
    # Anomaly detection risk
    features = np.array([[metrics['cpu'], metrics['memory']]])
    prediction = ai_engine.predict(features)[0]
    
    if prediction == -1:  # Anomaly detected
        risk += 25
    
    # Cap at 100
    risk = min(risk, 100)
    return max(risk, 0), prediction


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "WiFi SOC v7",
        "version": "7.0.0",
        "description": "Enterprise AI-powered Security Operations Center",
        "endpoints": [
            "/metrics",
            "/logs",
            "/alerts",
            "/statistics",
            "/processes",
            "/health"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_trained": ai_engine.trained
    }


@app.get("/metrics")
async def get_current_metrics():
    """
    Get current system metrics with AI anomaly detection
    Returns: CPU, Memory, Disk, Risk Score, Anomaly flag
    """
    global anomaly_count
    
    try:
        metrics = get_metrics()
        risk_score, anomaly = calculate_risk_score(metrics)
        
        # Update counters
        risk_history.append(risk_score)
        if len(risk_history) > 1000:
            risk_history.pop(0)
        
        if anomaly == -1:
            anomaly_count += 1
            insert_alert(
                alert_type="ANOMALY_DETECTED",
                severity="WARNING",
                message=f"System anomaly detected - CPU: {metrics['cpu']}%, Mem: {metrics['memory']}%",
                metrics=metrics
            )
        
        # Store in database
        insert_log(
            cpu=metrics['cpu'],
            memory=metrics['memory'],
            disk=metrics['disk'],
            risk_score=risk_score,
            anomaly=1 if anomaly == -1 else 0
        )
        
        return {
            "timestamp": metrics['timestamp'],
            "cpu": metrics['cpu'],
            "memory": metrics['memory'],
            "disk": metrics['disk'],
            "risk_score": risk_score,
            "anomaly": int(anomaly == -1),
            "anomaly_count": anomaly_count,
            "avg_risk": round(np.mean(risk_history), 2) if risk_history else 0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs")
async def get_logs(limit: int = 100):
    """Get recent SOC logs"""
    try:
        logs = get_recent_logs(limit)
        return {
            "count": len(logs),
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts")
async def get_alerts(limit: int = 50):
    """Get recent security alerts"""
    try:
        alerts = get_recent_alerts(limit)
        return {
            "count": len(alerts),
            "alerts": alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics")
async def get_soc_statistics():
    """Get SOC statistics and summaries"""
    try:
        stats = get_statistics()
        return {
            **stats,
            "anomaly_detections": anomaly_count,
            "avg_risk_history": round(np.mean(risk_history), 2) if risk_history else 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/processes")
async def get_top_processes():
    """Get top processes by CPU and Memory usage"""
    try:
        processes = get_process_info()
        return {
            "count": len(processes),
            "processes": processes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard")
async def dashboard_data():
    """Get all dashboard data in one request"""
    try:
        metrics = await get_current_metrics()
        stats = get_statistics()
        processes = get_process_info()
        alerts = get_recent_alerts(5)
        
        return {
            "metrics": metrics,
            "statistics": stats,
            "top_processes": processes,
            "recent_alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
