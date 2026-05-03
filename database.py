"""
SQLite Database for SOC Logging
Stores all security events and metrics
"""
import sqlite3
from datetime import datetime
import os

DB_PATH = "data/soc.db"


def init_database():
    """Initialize SQLite database with required tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create logs table
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu REAL,
            memory REAL,
            disk REAL,
            risk_score INTEGER,
            anomaly INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create alerts table
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            alert_type TEXT,
            severity TEXT,
            message TEXT,
            metrics TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✓ Database initialized")


def insert_log(cpu, memory, disk, risk_score, anomaly):
    """Insert a security log entry"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO logs (timestamp, cpu, memory, disk, risk_score, anomaly)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        cpu,
        memory,
        disk,
        risk_score,
        anomaly
    ))
    
    conn.commit()
    conn.close()


def insert_alert(alert_type, severity, message, metrics=None):
    """Insert security alert"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO alerts (timestamp, alert_type, severity, message, metrics)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        alert_type,
        severity,
        message,
        str(metrics) if metrics else None
    ))
    
    conn.commit()
    conn.close()


def get_recent_logs(limit=100):
    """Get recent logs"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("""
        SELECT * FROM logs
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_recent_alerts(limit=50):
    """Get recent alerts"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("""
        SELECT * FROM alerts
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_statistics():
    """Get SOC statistics"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) as total_logs FROM logs")
    total_logs = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) as critical_alerts FROM alerts WHERE severity='CRITICAL'")
    critical_alerts = c.fetchone()[0]
    
    c.execute("SELECT AVG(risk_score) as avg_risk FROM logs")
    avg_risk = c.fetchone()[0] or 0
    
    c.execute("SELECT AVG(cpu) as avg_cpu FROM logs")
    avg_cpu = c.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total_logs": total_logs,
        "critical_alerts": critical_alerts,
        "avg_risk": round(avg_risk, 2),
        "avg_cpu": round(avg_cpu, 2)
    }
