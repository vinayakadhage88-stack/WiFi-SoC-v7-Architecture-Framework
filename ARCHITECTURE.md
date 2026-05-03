"""
WiFi SOC v7 - SYSTEM ARCHITECTURE
==================================

ENTERPRISE SIEM PLATFORM
"""

# ╔═══════════════════════════════════════════════════════════════════╗
# ║                     SYSTEM ARCHITECTURE v7                        ║
# ╚═══════════════════════════════════════════════════════════════════╝

# LAYER 1: DATA COLLECTION
# ========================
┌─────────────────────────────────────┐
│     SYSTEM METRICS COLLECTOR        │
├─────────────────────────────────────┤
│  • CPU Usage (psutil)               │
│  • Memory Usage (psutil)            │
│  • Disk Usage (psutil)              │
│  • Process Info (top 10 by CPU)     │
│  • Network Stats (sent/recv)        │
│  • WiFi Info (netsh on Windows)     │
└──────────────┬──────────────────────┘
               │
               ↓ (triggered every 2 seconds)
               │
# LAYER 2: BACKEND SERVER
# ========================
┌──────────────────────────────────────┐
│         FASTAPI WEB SERVER           │
│         (backend/main.py)            │
├──────────────────────────────────────┤
│  Endpoints:                          │
│  • GET /metrics                      │
│  • GET /logs                         │
│  • GET /alerts                       │
│  • GET /statistics                   │
│  • GET /processes                    │
│  • GET /dashboard                    │
│  • GET /health                       │
│  • GET /docs (Swagger UI)            │
└──────────────┬───────────────────────┘
               │
       ┌───────┴───────┐
       ↓               ↓
# LAYER 3A: AI ENGINE        # LAYER 3B: DATABASE
# ========================   # ====================
┌──────────────────────┐   ┌──────────────────┐
│  ANOMALY DETECTION   │   │  SQLITE LOGS     │
│ (ai_engine.py)       │   │ (database.py)    │
├──────────────────────┤   ├──────────────────┤
│ Isolation Forest     │   │ Table: logs      │
│ • Train on baseline  │   │ • timestamp      │
│ • Detect anomalies   │   │ • cpu/mem/disk   │
│ • Return: -1 or 1    │   │ • risk_score     │
│ • Auto-retrain @100  │   │ • anomaly flag   │
│   samples            │   │                  │
│                      │   │ Table: alerts    │
│ Risk Calculation:    │   │ • alert_type     │
│ Base: 25             │   │ • severity       │
│ + CPU: 0-30          │   │ • message        │
│ + Memory: 0-25       │   │ • metrics JSON   │
│ + Disk: 0-20         │   │ • timestamp      │
│ + Anomaly: 0/25      │   │                  │
│ = Total: 0-100       │   └──────────────────┘
└──────────────────────┘

# LAYER 4: RESPONSE FORMATTING
# ============================
┌────────────────────────────────────────┐
│   RESPONSE OBJECT (JSON)               │
├────────────────────────────────────────┤
│ {                                      │
│   "cpu": 45.2,                         │
│   "memory": 62.1,                      │
│   "disk": 71.5,                        │
│   "risk_score": 38,                    │
│   "anomaly": 0,                        │
│   "timestamp": "2026-05-02T10:30:45"   │
│ }                                      │
└────────────────────────┬───────────────┘
                         │
                         ↓ (HTTP JSON)
                         │
# LAYER 5: WEB FRONTEND
# ======================
┌──────────────────────────────────────┐
│     HTML5 + VANILLA JAVASCRIPT       │
│      (frontend/index.html)           │
├──────────────────────────────────────┤
│  fetch() every 2 seconds             │
│  Parse JSON response                 │
│  Update DOM elements                 │
│  Render risk chart (Canvas API)      │
│  Update progress bars                │
│  Color code metrics                  │
└──────────────────────────────────────┘

# LAYER 6: USER INTERFACE
# ========================
┌────────────────────────────────────────────┐
│            DASHBOARD (Browser)             │
├────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌──────────────────┐ │
│ │ METRICS PANEL   │  │ ALERTS PANEL     │ │
│ ├─────────────────┤  ├──────────────────┤ │
│ │ CPU: [====] 45% │  │ Anomalies: 2     │ │
│ │ Mem: [======]62%│  │ Critical: 5      │ │
│ │ Disk:[====] 71% │  │ Status: Normal ✓ │ │
│ │ Risk: [==] 38   │  │ Alerts List      │ │
│ └─────────────────┘  └──────────────────┘ │
│ ┌────────────────────────────────────┐    │
│ │ STATISTICS & PROCESSES             │    │
│ ├────────────────────────────────────┤    │
│ │ Total Logs: 1250                   │    │
│ │ Top Processes:                     │    │
│ │ • chrome.exe (18.5%, 12.3%)        │    │
│ │ • python.exe (5.2%, 3.1%)          │    │
│ └────────────────────────────────────┘    │
│ ┌────────────────────────────────────┐    │
│ │ RISK SCORE HISTORY (CANVAS CHART)  │    │
│ │        ╱╲    ╱╲                     │    │
│ │       ╱  ╲  ╱  ╲                    │    │
│ │      ╱    ╲╱    ╲                   │    │
│ └────────────────────────────────────┘    │
└────────────────────────────────────────────┘

# ╔═══════════════════════════════════════════════════════════════════╗
# ║              DATA FLOW DIAGRAM (Request → Response)              ║
# ╚═══════════════════════════════════════════════════════════════════╝

Browser (app.js)
    │
    ├─ setInterval(fetchDashboardData, 2000)
    │
    ├─ fetch(API_BASE/metrics)
    │
    └─→ [HTTP GET REQUEST]
             │
             ↓
    FastAPI Backend (main.py)
             │
             ├─→ get_current_metrics()
             │
             ├─→ get_metrics() [collector.py]
             │   • CPU, Memory, Disk, Processes
             │
             ├─→ calculate_risk_score()
             │   • Base: 25
             │   • Add CPU/Memory/Disk risk
             │   • Check anomaly
             │   • Cap at 100
             │
             ├─→ ai_engine.predict() [ai_engine.py]
             │   • Isolation Forest model
             │   • Returns -1 (anomaly) or 1
             │
             ├─→ insert_log() [database.py]
             │   • Store in SQLite
             │
             ├─→ if anomaly:
             │       insert_alert()
             │
             └─→ return JSON
                     │
                     ↓ [HTTP 200 JSON]
                     │
Browser (app.js)
    │
    ├─ updateMetrics(data)
    ├─ updateStatistics(stats)
    ├─ updateAlerts(alerts)
    ├─ updateProcesses(processes)
    ├─ updateRiskChart(metrics)
    │
    └─→ DOM Updated
        • Progress bars animated
        • Color-coded
        • Chart redrawn
        • Live counter updated

# ╔═══════════════════════════════════════════════════════════════════╗
# ║                    DEPLOYMENT ARCHITECTURE                       ║
# ╚═══════════════════════════════════════════════════════════════════╝

# OPTION 1: LOCAL DEVELOPMENT
┌─────────────────────────────────────┐
│     YOUR COMPUTER                   │
├─────────────────────────────────────┤
│  Backend: http://127.0.0.1:8000     │
│  Frontend: file://...               │
│  Database: data/soc.db (local)      │
└─────────────────────────────────────┘

# OPTION 2: LOCAL SERVER
┌─────────────────────────────────────┐
│     SERVER / VM                     │
├─────────────────────────────────────┤
│  Backend: http://server-ip:8000     │
│  Frontend: http://server-ip:8080    │
│  Database: data/soc.db              │
└─────────────────────────────────────┘

# OPTION 3: DOCKER CONTAINERIZED
┌─────────────────────────────────────┐
│     DOCKER CONTAINER                │
├─────────────────────────────────────┤
│  ┌─────────────────────────────────┐│
│  │ Backend (Gunicorn)              ││
│  │ Database (SQLite or PG)         ││
│  │ Frontend (Static files)         ││
│  └─────────────────────────────────┘│
│  Port: 8000 (exposed)               │
└─────────────────────────────────────┘

# OPTION 4: CLOUD DEPLOYMENT
┌──────────────────────────────────────────┐
│         CLOUD PROVIDER                   │
├──────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐ │
│  │ Load Balancer                       │ │
│  └──────────┬────────────────────────┬┘ │
│             │                        │   │
│    ┌────────▼─────┐        ┌────────▼──┐│
│    │ API Gateway  │        │CloudFront ││
│    └────────┬─────┘        └─────┬──────┘│
│             │                    │       │
│    ┌────────▼──────────────────┐ │       │
│    │ Serverless Functions      │ │       │
│    │ (Lambda/Cloud Functions)  │ │       │
│    └────────┬───────────────────┘ │       │
│             │                     │       │
│    ┌────────▼────────────────────┬┘       │
│    │ Managed Database            │        │
│    │ (RDS/CloudSQL/Firestore)    │        │
│    └─────────────────────────────┘        │
└──────────────────────────────────────────┘

# ╔═══════════════════════════════════════════════════════════════════╗
# ║                  SCALING ARCHITECTURE                            ║
# ╚═══════════════════════════════════════════════════════════════════╝

# SINGLE INSTANCE (Current)
┌────────────────────┐
│  FastAPI + SQLite  │
│  Max: ~1000 req/s  │
└────────────────────┘

# SCALED VERSION
┌─────────────────┐
│ Load Balancer   │
├─────────────────┤
│ FastAPI x 4     │
│ (separate proc) │
└────────┬────────┘
         │
    ┌────▼─────┐
    │PostgreSQL│
    │(managed) │
    └──────────┘

# FULL ENTERPRISE
┌──────────────────────────────────────┐
│        Multiple Data Centers         │
├──────────────────────────────────────┤
│  ┌────────────┐    ┌────────────┐   │
│  │ Region A   │    │ Region B   │   │
│  │ (FastAPI x4)    │(FastAPI x4)│   │
│  └───┬────────┘    └────┬───────┘   │
│      │                  │           │
│      └──────────┬───────┘           │
│                 ↓                    │
│      ┌──────────────────┐           │
│      │  PostgreSQL      │           │
│      │  Multi-region    │           │
│      │  Replication     │           │
│      └──────────────────┘           │
│                                     │
│      ┌──────────────────┐           │
│      │  Redis Cache     │           │
│      │  (session/cache) │           │
│      └──────────────────┘           │
│                                     │
│      ┌──────────────────┐           │
│      │ Message Queue    │           │
│      │ (RabbitMQ/Kafka) │           │
│      └──────────────────┘           │
└──────────────────────────────────────┘

# ╔═══════════════════════════════════════════════════════════════════╗
# ║              MONITORING & OBSERVABILITY STACK                    ║
# ╚═══════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────┐
│      APPLICATION METRICS            │
├─────────────────────────────────────┤
│  • API response times               │
│  • Request counts                   │
│  • Error rates                      │
│  • Database query times             │
│  • Cache hit/miss rates             │
└─────────────────────────────────────┘
         │
         ├─→ Prometheus (collection)
         │
         ├─→ Grafana (visualization)
         │
         └─→ AlertManager (alerting)

┌─────────────────────────────────────┐
│      APPLICATION LOGS               │
├─────────────────────────────────────┤
│  • Request logs                     │
│  • Error logs                       │
│  • Debug logs                       │
│  • Audit logs                       │
└─────────────────────────────────────┘
         │
         ├─→ ELK Stack
         │   • Elasticsearch
         │   • Logstash
         │   • Kibana
         │
         └─→ CloudWatch / Stackdriver

┌─────────────────────────────────────┐
│      DISTRIBUTED TRACING            │
├─────────────────────────────────────┤
│  • Request traces                   │
│  • Service latency                  │
│  • Dependency mapping               │
└─────────────────────────────────────┘
         │
         ├─→ Jaeger
         ├─→ Zipkin
         └─→ AWS X-Ray

# ╔═══════════════════════════════════════════════════════════════════╗
# ║                COMPONENT INTERACTION MATRIX                      ║
# ╚═══════════════════════════════════════════════════════════════════╝

              |Main|AI |Collector|DB |Frontend
──────────────┼────┼───┼─────────┼───┼────────
Main          | -  |✓  |✓        |✓  |← HTTP
AI            |    | - |         |   |
Collector     |    |   | -       |   |
DB            |    |   |         | - |
Frontend      |✓ →*|   |         |   | -

* = HTTP calls to /metrics, /logs, /alerts, etc.

# ╔═══════════════════════════════════════════════════════════════════╗
# ║                    REQUEST/RESPONSE CYCLE                        ║
# ╚═══════════════════════════════════════════════════════════════════╝

T0: Browser sends GET /metrics
    │
T50ms: FastAPI receives request
    ├─ Call collector.get_metrics() [T50-80ms]
    ├─ Call ai_engine.predict() [T80-100ms]
    ├─ Calculate risk_score() [T100-110ms]
    ├─ insert_log() to database [T110-130ms]
    └─ Prepare JSON response [T130-150ms]
    │
T200ms: Browser receives JSON
    ├─ Parse JSON
    ├─ Update DOM elements
    ├─ Animate progress bars
    ├─ Redraw chart
    └─ Update status indicators
    │
T2000ms: Next fetch cycle (setInterval)

# ╔═══════════════════════════════════════════════════════════════════╗
# ║                     TECHNOLOGY STACK DIAGRAM                     ║
# ╚═══════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────┐
│                    WiFi SOC v7 Stack                         │
├──────────────────────────────────────────────────────────────┤
│ Layer     │ Technology      │ Version   │ Purpose             │
├───────────┼─────────────────┼───────────┼─────────────────────┤
│ Frontend  │ HTML5           │ ES2020    │ UI Framework        │
│           │ CSS3            │ ES2020    │ Styling             │
│           │ Vanilla JS      │ ES2020    │ Interactions        │
├───────────┼─────────────────┼───────────┼─────────────────────┤
│ Backend   │ Python 3.8+     │ 3.10      │ Runtime             │
│           │ FastAPI         │ 0.104.1   │ Web Framework       │
│           │ Uvicorn         │ 0.24.0    │ ASGI Server         │
├───────────┼─────────────────┼───────────┼─────────────────────┤
│ ML/AI     │ Scikit-learn    │ 1.3.2     │ ML Models           │
│           │ NumPy           │ 1.24.3    │ Numerical Compute   │
├───────────┼─────────────────┼───────────┼─────────────────────┤
│ System    │ psutil          │ 5.9.6     │ OS Metrics          │
│ Monitor   │ subprocess      │ Built-in  │ Shell Commands      │
├───────────┼─────────────────┼───────────┼─────────────────────┤
│ Database  │ SQLite3         │ Built-in  │ Relational DB       │
└──────────────────────────────────────────────────────────────┘

---
Built with ❤️ for Enterprise Security Operations
