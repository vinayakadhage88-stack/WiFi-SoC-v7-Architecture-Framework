"""
WiFi SOC v7 - Standalone Backend Server
Run this directly for quick testing without uvicorn CLI
"""

if __name__ == "__main__":
    import uvicorn
    from backend.main import app
    
    print("\n")
    print("=" * 60)
    print("  🧠 WiFi SOC v7 - Enterprise SOC Platform")
    print("=" * 60)
    print("\n  Backend: http://127.0.0.1:8000")
    print("  Docs:    http://127.0.0.1:8000/docs")
    print("  ReDoc:   http://127.0.0.1:8000/redoc")
    print("\n" + "=" * 60)
    print("\n  Press Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
