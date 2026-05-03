/**
 * SOC Dashboard - Live Update Engine
 * Fetches data from FastAPI backend and updates UI in real-time
 */

const API_BASE = "http://127.0.0.1:8000";
const REFRESH_INTERVAL = 2000; // 2 seconds
let riskHistory = [];
let chartCanvas = null;
let chartContext = null;

// ========== INITIALIZATION ==========
function initDashboard() {
    console.log("🚀 Initializing SOC Dashboard v7");
    chartCanvas = document.getElementById('risk-chart');
    chartContext = chartCanvas.getContext('2d');
    
    // Initial fetch
    fetchDashboardData();
    
    // Setup refresh interval
    setInterval(fetchDashboardData, REFRESH_INTERVAL);
}

// ========== FETCH DATA ==========
async function fetchDashboardData() {
    try {
        // Fetch all data in parallel
        const [metricsRes, logsRes, statsRes, alertsRes, processesRes] = await Promise.all([
            fetch(`${API_BASE}/metrics`),
            fetch(`${API_BASE}/logs?limit=20`),
            fetch(`${API_BASE}/statistics`),
            fetch(`${API_BASE}/alerts?limit=5`),
            fetch(`${API_BASE}/processes`)
        ]);

        if (!metricsRes.ok) throw new Error(`Metrics API error: ${metricsRes.status}`);
        if (!statsRes.ok) throw new Error(`Stats API error: ${statsRes.status}`);
        if (!alertsRes.ok) throw new Error(`Alerts API error: ${alertsRes.status}`);
        if (!processesRes.ok) throw new Error(`Processes API error: ${processesRes.status}`);

        const metrics = await metricsRes.json();
        const stats = await statsRes.json();
        const alerts = await alertsRes.json();
        const processes = await processesRes.json();

        // Update UI
        updateMetrics(metrics);
        updateStatistics(stats);
        updateAlerts(alerts);
        updateProcesses(processes);
        updateRiskChart(metrics);
        updateConnectionStatus(true);

    } catch (error) {
        console.error("❌ Fetch error:", error);
        updateConnectionStatus(false);
        showError(error.message);
    }
}

// ========== UPDATE METRICS ==========
function updateMetrics(data) {
    // CPU
    const cpuValue = data.cpu.toFixed(1);
    document.getElementById('cpu-value').textContent = cpuValue + '%';
    document.getElementById('cpu-bar').style.width = cpuValue + '%';
    
    // Memory
    const memValue = data.memory.toFixed(1);
    document.getElementById('mem-value').textContent = memValue + '%';
    document.getElementById('mem-bar').style.width = memValue + '%';
    
    // Disk
    const diskValue = data.disk.toFixed(1);
    document.getElementById('disk-value').textContent = diskValue + '%';
    document.getElementById('disk-bar').style.width = diskValue + '%';
    
    // Risk Score
    const riskValue = data.risk_score;
    document.getElementById('risk-value').textContent = riskValue;
    document.getElementById('risk-gauge').style.width = riskValue + '%';
    
    // Color coding for risk
    const riskCard = document.querySelector('.risk-card');
    if (riskValue > 70) {
        riskCard.style.borderColor = '#ef4444';
        riskCard.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(251, 146, 60, 0.15) 100%)';
    } else if (riskValue > 40) {
        riskCard.style.borderColor = '#f59e0b';
        riskCard.style.background = 'linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 146, 60, 0.1) 100%)';
    } else {
        riskCard.style.borderColor = '#10b981';
        riskCard.style.background = 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(34, 197, 94, 0.1) 100%)';
    }
    
    // Alert status
    document.getElementById('anomaly-count').textContent = data.anomaly_count;
    
    // Update alert message
    const alertMsg = document.getElementById('alert-message');
    if (data.anomaly === 1) {
        alertMsg.textContent = '🚨 ANOMALY DETECTED!';
        alertMsg.classList.add('anomaly');
    } else {
        alertMsg.textContent = '✅ System Normal';
        alertMsg.classList.remove('anomaly');
    }
    
    // Store for chart
    riskHistory.push(riskValue);
    if (riskHistory.length > 100) {
        riskHistory.shift();
    }
    
    // Update timestamp
    updateLastUpdate();
}

// ========== UPDATE STATISTICS ==========
function updateStatistics(stats) {
    document.getElementById('total-logs').textContent = stats.total_logs;
    document.getElementById('critical-count').textContent = stats.critical_alerts;
    document.getElementById('avg-risk').textContent = stats.avg_risk;
    document.getElementById('avg-cpu').textContent = stats.avg_cpu.toFixed(1) + '%';
    document.getElementById('total-alerts').textContent = stats.critical_alerts;
}

// ========== UPDATE ALERTS ==========
function updateAlerts(alertsData) {
    const alertsList = document.getElementById('alerts-list');
    
    if (alertsData.alerts.length === 0) {
        alertsList.innerHTML = '<div class="alert-item">No recent alerts</div>';
        return;
    }
    
    alertsList.innerHTML = alertsData.alerts.map(alert => {
        const time = new Date(alert.timestamp).toLocaleTimeString();
        const isCritical = alert.severity === 'CRITICAL';
        return `
            <div class="alert-item ${isCritical ? 'critical' : ''}">
                <div class="alert-time">${time}</div>
                <div class="alert-text">
                    <strong>${alert.alert_type}</strong><br>
                    ${alert.message}
                </div>
            </div>
        `;
    }).join('');
}

// ========== UPDATE PROCESSES ==========
function updateProcesses(processesData) {
    const processesList = document.getElementById('processes-list');
    
    if (processesData.processes.length === 0) {
        processesList.innerHTML = '<div class="loading">No processes data</div>';
        return;
    }
    
    processesList.innerHTML = processesData.processes.slice(0, 8).map(proc => `
        <div class="process-item">
            <div class="process-name">${proc.name}</div>
            <div class="process-stats">
                CPU: ${proc.cpu.toFixed(1)}% | Mem: ${proc.memory.toFixed(1)}%
            </div>
        </div>
    `).join('');
}

// ========== UPDATE RISK CHART ==========
function updateRiskChart(metrics) {
    if (!chartContext || !chartCanvas) return;
    
    const width = chartCanvas.width;
    const height = chartCanvas.height;
    
    // Clear canvas
    chartContext.fillStyle = '#0f172a';
    chartContext.fillRect(0, 0, width, height);
    
    // Draw grid
    chartContext.strokeStyle = '#334155';
    chartContext.lineWidth = 1;
    
    for (let i = 0; i <= 4; i++) {
        const y = (height / 4) * i;
        chartContext.beginPath();
        chartContext.moveTo(0, y);
        chartContext.lineTo(width, y);
        chartContext.stroke();
    }
    
    if (riskHistory.length < 2) return;
    
    // Draw risk line
    const pointWidth = width / (riskHistory.length - 1);
    const maxRisk = 100;
    
    chartContext.strokeStyle = '#ef4444';
    chartContext.lineWidth = 2;
    chartContext.beginPath();
    
    riskHistory.forEach((risk, index) => {
        const x = index * pointWidth;
        const y = height - (risk / maxRisk) * height;
        
        if (index === 0) {
            chartContext.moveTo(x, y);
        } else {
            chartContext.lineTo(x, y);
        }
    });
    
    chartContext.stroke();
    
    // Draw area under curve
    chartContext.fillStyle = 'rgba(239, 68, 68, 0.2)';
    chartContext.lineTo(width, height);
    chartContext.lineTo(0, height);
    chartContext.fill();
    
    // Draw current point
    const lastRisk = riskHistory[riskHistory.length - 1];
    const lastX = width;
    const lastY = height - (lastRisk / maxRisk) * height;
    
    chartContext.fillStyle = '#ef4444';
    chartContext.beginPath();
    chartContext.arc(lastX, lastY, 4, 0, Math.PI * 2);
    chartContext.fill();
    
    // Draw risk value text
    chartContext.fillStyle = '#f1f5f9';
    chartContext.font = 'bold 16px Arial';
    chartContext.textAlign = 'right';
    chartContext.fillText(lastRisk.toFixed(0), width - 10, lastY - 15);
}

// ========== CONNECTION STATUS ==========
function updateConnectionStatus(connected) {
    const status = document.getElementById('connection-status');
    if (connected) {
        status.textContent = '● Connected';
        status.style.color = '#10b981';
    } else {
        status.textContent = '● Disconnected';
        status.style.color = '#ef4444';
    }
}

// ========== ERROR HANDLING ==========
function showError(message) {
    console.error("Dashboard error:", message);
    // Could show a toast notification here
}

// ========== UPDATE TIMESTAMP ==========
function updateLastUpdate() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('last-update').textContent = timeString;
}

// ========== START DASHBOARD ==========
document.addEventListener('DOMContentLoaded', initDashboard);

console.log("📊 SOC Dashboard v7 loaded and ready");
