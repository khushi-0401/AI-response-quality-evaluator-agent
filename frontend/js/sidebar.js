// =============================================
// SIDEBAR - Connected to Backend
// =============================================

// =============================================
// FETCH STATS FROM BACKEND
// =============================================

async function fetchSidebarStats() {
    try {
        const response = await fetch('http://localhost:8000/api/stats');
        if (!response.ok) {
            throw new Error('Failed to fetch stats');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching sidebar stats:', error);
        return null;
    }
}

// =============================================
// UPDATE SIDEBAR WITH REAL DATA
// =============================================

function updateSidebar(data) {
    // Get all sidebar elements
    const totalEl = document.getElementById('sidebarTotal');
    const passEl = document.getElementById('sidebarPass');
    const improveEl = document.getElementById('sidebarImprove');
    const failEl = document.getElementById('sidebarFail');
    const historyEl = document.getElementById('historyList');

    if (!data) {
        // Show empty state if no data
        if (totalEl) totalEl.textContent = '0';
        if (passEl) passEl.textContent = '0';
        if (improveEl) improveEl.textContent = '0';
        if (failEl) failEl.textContent = '0';
        if (historyEl) {
            historyEl.innerHTML = `
                <div class="no-history">No evaluations yet</div>
            `;
        }
        return;
    }

    // Update stats
    if (totalEl) totalEl.textContent = data.total || 0;
    if (passEl) passEl.textContent = data.pass || 0;
    if (improveEl) improveEl.textContent = data.needs_improvement || 0;
    if (failEl) failEl.textContent = data.fail || 0;

    // Update recent history
    if (!historyEl) return;
    
    if (!data.recent || data.recent.length === 0) {
        historyEl.innerHTML = `
            <div class="no-history">No evaluations yet</div>
        `;
        return;
    }

    // Show last 5 evaluations
    historyEl.innerHTML = data.recent.map(item => {
        // Determine verdict class
        let verdictClass = 'improve';
        let scoreClass = 'improve';
        if (item.verdict === 'PASS') {
            verdictClass = 'pass';
            scoreClass = 'pass';
        } else if (item.verdict === 'FAIL') {
            verdictClass = 'fail';
            scoreClass = 'fail';
        }
        
        return `
            <div class="history-item ${verdictClass}" onclick="loadHistoryItem('${item.id}')">
                <div class="h-q">${item.question}</div>
                <div class="h-meta">
                    <span>${item.timestamp || 'N/A'}</span>
                    <span class="h-score ${scoreClass}">${Math.round(item.score * 100)}%</span>
                </div>
            </div>
        `;
    }).join('');
}

// =============================================
// LOAD HISTORY ITEM (Placeholder)
// =============================================

function loadHistoryItem(id) {
    alert(`Loading evaluation: ${id}\n\nIn the future, this will load the full evaluation details.`);
}

// =============================================
// SIDEBAR INIT
// =============================================

async function initSidebar() {
    const data = await fetchSidebarStats();
    updateSidebar(data);
}

// =============================================
// EXPOSE FUNCTIONS
// =============================================

window.loadHistoryItem = loadHistoryItem;
window.updateSidebar = updateSidebar;
window.initSidebar = initSidebar;

// =============================================
// AUTO-INIT ON PAGE LOAD
// =============================================

document.addEventListener('DOMContentLoaded', function() {
    initSidebar();
});