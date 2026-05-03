"""
System Metrics Collector
Gathers CPU, Memory, and Network data
"""
import psutil
import subprocess
from datetime import datetime


def get_metrics():
    """
    Collect system metrics
    Returns dict with CPU, Memory, and Network data
    """
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    # Get network stats
    net_stats = psutil.net_io_counters()
    
    # Try to get WiFi info (Windows specific)
    wifi_info = "N/A"
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            wifi_info = result.stdout[:200]  # First 200 chars
    except Exception as e:
        wifi_info = str(e)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": round(cpu, 2),
        "memory": round(memory, 2),
        "disk": round(disk, 2),
        "network_sent": net_stats.bytes_sent,
        "network_recv": net_stats.bytes_recv,
        "wifi_info": wifi_info
    }


def get_process_info():
    """Get top processes by CPU and Memory"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu': proc.info['cpu_percent'],
                'memory': proc.info['memory_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by CPU and return top 10
    processes.sort(key=lambda x: x['cpu'], reverse=True)
    return processes[:10]
