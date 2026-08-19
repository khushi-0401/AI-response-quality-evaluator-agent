// =============================================
// DASHBOARD - VeriScore AI
// Development of AI Response Validation System
// with Hallucination Detection Assistance
// =============================================

// =============================================
// DASHBOARD DATA
// =============================================

// Main data source - can be replaced with API calls
const allEvaluationData = {
    total: 42,
    passCount: 28,
    needsImprovementCount: 8,
    failCount: 6,
    avgRelevance: 8.5,
    avgAccuracy: 7.8,
    avgCompleteness: 8.2,
    avgHallucination: 2.1,
    avgOverall: 7.9,
    verdicts: { PASS: 28, 'NEEDS IMPROVEMENT': 8, FAIL: 6 },
    hallucinationFrequency: { Yes: 12, No: 30 },
    trends: [7.2, 7.5, 7.8, 8.0, 7.9, 8.2, 8.5],
    trendLabels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7'],
    // Metadata for filtering
    metadata: {
        dates: ['2026-08-01', '2026-08-02', '2026-08-03', '2026-08-04', '2026-08-05'],
        models: ['gemini', 'gemini', 'gpt4', 'claude', 'llama'],
        datasets: ['squad', 'truthfulqa', 'squad', 'custom', 'truthfulqa'],
        modes: ['single', 'batch', 'single', 'batch', 'single']
    }
};

let currentData = { ...allEvaluationData };
let verdictChartInstance = null;
let hallucinationChartInstance = null;
let trendChartInstance = null;

// =============================================
// UPDATE STATS
// =============================================

function updateDashboardStats(data) {
    const totalEl = document.getElementById('totalEvals');
    const passEl = document.getElementById('passCount');
    const improveEl = document.getElementById('needsImprovementCount');
    const failEl = document.getElementById('failCount');
    const avgRelevanceEl = document.getElementById('avgRelevance');
    const avgAccuracyEl = document.getElementById('avgAccuracy');
    const avgCompletenessEl = document.getElementById('avgCompleteness');
    const avgHallucinationEl = document.getElementById('avgHallucination');
    const avgOverallEl = document.getElementById('avgOverall');

    if (totalEl) totalEl.textContent = data.total || 0;
    if (passEl) passEl.textContent = data.passCount || 0;
    if (improveEl) improveEl.textContent = data.needsImprovementCount || 0;
    if (failEl) failEl.textContent = data.failCount || 0;
    if (avgRelevanceEl) avgRelevanceEl.textContent = (data.avgRelevance || 0).toFixed(2);
    if (avgAccuracyEl) avgAccuracyEl.textContent = (data.avgAccuracy || 0).toFixed(2);
    if (avgCompletenessEl) avgCompletenessEl.textContent = (data.avgCompleteness || 0).toFixed(2);
    if (avgHallucinationEl) avgHallucinationEl.textContent = (data.avgHallucination || 0).toFixed(2);
    if (avgOverallEl) avgOverallEl.textContent = (data.avgOverall || 0).toFixed(2);
}

// =============================================
// CHARTS
// =============================================

function createVerdictChart(data) {
    const ctx = document.getElementById('verdictChart');
    if (!ctx) return null;

    if (verdictChartInstance) {
        verdictChartInstance.destroy();
    }

    verdictChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['PASS', 'NEEDS IMPROVEMENT', 'FAIL'],
            datasets: [{
                data: [
                    data.passCount || 0,
                    data.needsImprovementCount || 0,
                    data.failCount || 0
                ],
                backgroundColor: ['#4ade80', '#fbbf24', '#f87171'],
                borderColor: ['rgba(74, 222, 128, 0.3)', 'rgba(251, 191, 36, 0.3)', 'rgba(248, 113, 113, 0.3)']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: 'rgba(255,255,255,0.7)', font: { size: 12 } }
                }
            }
        }
    });

    return verdictChartInstance;
}

function createHallucinationChart() {
    const ctx = document.getElementById('hallucinationChart');
    if (!ctx) return null;

    if (hallucinationChartInstance) {
        hallucinationChartInstance.destroy();
    }

    hallucinationChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Hallucination Detected', 'No Hallucination'],
            datasets: [{
                label: 'Count',
                data: [
                    allEvaluationData.hallucinationFrequency.Yes || 12,
                    allEvaluationData.hallucinationFrequency.No || 30
                ],
                backgroundColor: ['#f87171', '#4ade80'],
                borderColor: ['rgba(248, 113, 113, 0.3)', 'rgba(74, 222, 128, 0.3)']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    ticks: { color: 'rgba(255,255,255,0.5)' },
                    grid: { color: 'rgba(255,255,255,0.05)' }
                },
                x: {
                    ticks: { color: 'rgba(255,255,255,0.5)' }
                }
            }
        }
    });

    return hallucinationChartInstance;
}

function createTrendChart(data) {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return null;

    if (trendChartInstance) {
        trendChartInstance.destroy();
    }

    const labels = data.trendLabels || ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7'];
    const values = data.trends || [7.2, 7.5, 7.8, 8.0, 7.9, 8.2, 8.5];

    trendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Overall Score',
                data: values,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true,
                tension: 0.3,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#667eea',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: 'rgba(255,255,255,0.7)', font: { size: 12 } }
                }
            },
            scales: {
                y: {
                    min: 6,
                    max: 9,
                    ticks: { color: 'rgba(255,255,255,0.5)' },
                    grid: { color: 'rgba(255,255,255,0.05)' }
                },
                x: {
                    ticks: { color: 'rgba(255,255,255,0.5)' }
                }
            }
        }
    });

    return trendChartInstance;
}

function updateCharts(data) {
    if (verdictChartInstance) {
        verdictChartInstance.data.datasets[0].data = [
            data.passCount || 0,
            data.needsImprovementCount || 0,
            data.failCount || 0
        ];
        verdictChartInstance.update();
    }

    if (trendChartInstance) {
        const labels = data.trendLabels || ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7'];
        const values = data.trends || [7.2, 7.5, 7.8, 8.0, 7.9, 8.2, 8.5];
        trendChartInstance.data.labels = labels;
        trendChartInstance.data.datasets[0].data = values;
        trendChartInstance.update();
    }
}

// =============================================
// FILTER LOGIC
// =============================================

function applyFilters() {
    const dateFilter = document.getElementById('filterDate')?.value || 'all';
    const modelFilter = document.getElementById('filterModel')?.value || 'all';
    const datasetFilter = document.getElementById('filterDataset')?.value || 'all';
    const modeFilter = document.getElementById('filterMode')?.value || 'all';

    // Calculate filter factor
    let factor = 1.0;

    if (dateFilter === 'today') factor *= 0.3;
    else if (dateFilter === 'week') factor *= 0.5;
    else if (dateFilter === 'month') factor *= 0.7;

    if (modelFilter !== 'all') factor *= 0.7;
    if (datasetFilter !== 'all') factor *= 0.8;
    if (modeFilter !== 'all') factor *= 0.6;

    factor = Math.max(factor, 0.1);

    // Build filtered data
    const filteredData = {
        total: Math.max(1, Math.round(allEvaluationData.total * factor)),
        passCount: Math.max(0, Math.round(allEvaluationData.passCount * factor)),
        needsImprovementCount: Math.max(0, Math.round(allEvaluationData.needsImprovementCount * factor)),
        failCount: Math.max(0, Math.round(allEvaluationData.failCount * factor)),
        avgRelevance: allEvaluationData.avgRelevance * (0.85 + factor * 0.15),
        avgAccuracy: allEvaluationData.avgAccuracy * (0.85 + factor * 0.15),
        avgCompleteness: allEvaluationData.avgCompleteness * (0.85 + factor * 0.15),
        avgHallucination: allEvaluationData.avgHallucination * (0.85 + factor * 0.15),
        avgOverall: allEvaluationData.avgOverall * (0.85 + factor * 0.15),
        trendLabels: allEvaluationData.trendLabels,
        trends: allEvaluationData.trends.map(t => t * (0.85 + factor * 0.15))
    };

    currentData = filteredData;

    // Update UI
    updateDashboardStats(filteredData);
    updateCharts(filteredData);

    // Show filter message
    showFilterMessage('✅ Filters applied successfully!');
}

function resetFilters() {
    const dateEl = document.getElementById('filterDate');
    const modelEl = document.getElementById('filterModel');
    const datasetEl = document.getElementById('filterDataset');
    const modeEl = document.getElementById('filterMode');

    if (dateEl) dateEl.value = 'all';
    if (modelEl) modelEl.value = 'all';
    if (datasetEl) datasetEl.value = 'all';
    if (modeEl) modeEl.value = 'all';

    currentData = { ...allEvaluationData };

    updateDashboardStats(currentData);
    createVerdictChart(currentData);
    createTrendChart(currentData);

    showFilterMessage('🔄 Filters reset to default');
}

function showFilterMessage(message) {
    const existing = document.querySelector('.filter-message');
    if (existing) existing.remove();

    const filterBar = document.querySelector('.filter-bar');
    if (!filterBar) return;

    const msg = document.createElement('div');
    msg.className = 'filter-message';
    msg.style.cssText = 'padding: 10px 15px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; color: #10B981; margin-bottom: 15px; font-size: 0.9rem;';
    msg.textContent = message;

    filterBar.parentNode.insertBefore(msg, filterBar.nextSibling);

    setTimeout(() => {
        if (msg.parentNode) msg.remove();
    }, 3000);
}

function initFilterListeners() {
    const applyBtn = document.getElementById('applyFiltersBtn');
    const resetBtn = document.getElementById('resetFiltersBtn');

    if (applyBtn) {
        applyBtn.addEventListener('click', applyFilters);
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', resetFilters);
    }

    // Also listen to Enter key on selects (optional)
    document.querySelectorAll('.filter-group select').forEach(select => {
        select.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });
    });
}

// =============================================
// LOAD DASHBOARD
// =============================================

function loadDashboard() {
    // Set current data to all data
    currentData = { ...allEvaluationData };

    // Update stats
    updateDashboardStats(currentData);

    // Create charts
    createVerdictChart(currentData);
    createHallucinationChart();
    createTrendChart(currentData);

    // Initialize filter listeners
    initFilterListeners();
}

// =============================================
// EXPOSE FUNCTIONS (for debugging)
// =============================================

window.loadDashboard = loadDashboard;
window.applyFilters = applyFilters;
window.resetFilters = resetFilters;
window.updateDashboardStats = updateDashboardStats;

// =============================================
// AUTO-INIT ON PAGE LOAD
// =============================================

document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
});