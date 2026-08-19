// =============================================
// UI COMPONENTS - VeriScore AI
// =============================================

function renderScores(result) {
    const container = document.getElementById('scores');
    if (!container) return;
    
    const scores = [
        { label: 'Relevance', value: result.relevance?.relevance_score || 0 },
        { label: 'Accuracy', value: result.accuracy?.accuracy_score || 0 },
        { label: 'Completeness', value: result.completeness?.completeness_score || 0 },
        { label: 'Hallucination', value: result.hallucination?.hallucination_score || 0 },
        { label: 'Overall', value: result.verdict?.overall_score || 0 }
    ];
    
    container.innerHTML = scores.map(s => `
        <div class="score-card">
            <h3>${s.label}</h3>
            <div class="value">${s.value.toFixed(2)}</div>
            <div class="badge ${s.value >= 0.7 ? 'badge-pass' : 'badge-fail'}">
                ${s.value >= 0.7 ? '✅ Pass' : '❌ Fail'}
            </div>
        </div>
    `).join('');
    
    renderDetails(result);
}

function renderDetails(result) {
    const container = document.getElementById('details');
    if (!container) return;
    
    const tabs = [
        { id: 'relevance', label: '📊 Relevance', data: result.relevance },
        { id: 'accuracy', label: '🎯 Accuracy', data: result.accuracy },
        { id: 'completeness', label: '📋 Completeness', data: result.completeness },
        { id: 'hallucination', label: '🚨 Hallucination', data: result.hallucination }
    ];
    
    container.innerHTML = `
        <div class="details-section">
            <div class="details-tabs">
                ${tabs.map(t => `<button class="details-tab ${t.id === 'relevance' ? 'active' : ''}" data-tab="${t.id}">${t.label}</button>`).join('')}
            </div>
            ${tabs.map(t => `
                <div class="detail-content ${t.id === 'relevance' ? 'active' : ''}" id="detail-${t.id}">
                    ${renderDetailContent(t.id, t.data)}
                </div>
            `).join('')}
        </div>
    `;
    
    document.querySelectorAll('.details-tab').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.details-tab').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.detail-content').forEach(d => d.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(`detail-${btn.dataset.tab}`).classList.add('active');
        });
    });
}

function renderDetailContent(type, data) {
    if (!data) return '<p>No data available</p>';
    
    switch(type) {
        case 'relevance':
            return `
                <p><strong>Score:</strong> ${(data.relevance_score || 0).toFixed(2)}</p>
                <p><strong>Reasoning:</strong> ${data.reasoning || 'N/A'}</p>
                ${data.key_points_covered?.length ? `<p><strong>✅ Covered:</strong> ${data.key_points_covered.join(', ')}</p>` : ''}
                ${data.missing_points?.length ? `<p><strong>❌ Missing:</strong> ${data.missing_points.join(', ')}</p>` : ''}
            `;
        case 'accuracy':
            return `
                <p><strong>Score:</strong> ${(data.accuracy_score || 0).toFixed(2)}</p>
                <p><strong>Evidence:</strong> ${data.evidence || 'N/A'}</p>
                ${data.correct_claims?.length ? `<p><strong>✅ Correct:</strong> ${data.correct_claims.join(', ')}</p>` : ''}
                ${data.incorrect_claims?.length ? `<p><strong>❌ Incorrect:</strong> ${data.incorrect_claims.join(', ')}</p>` : ''}
            `;
        case 'completeness':
            return `
                <p><strong>Score:</strong> ${(data.completeness_score || 0).toFixed(2)}</p>
                <p><strong>Reasoning:</strong> ${data.reasoning || 'N/A'}</p>
                ${data.covered_aspects?.length ? `<p><strong>✅ Covered:</strong> ${data.covered_aspects.join(', ')}</p>` : ''}
                ${data.missing_aspects?.length ? `<p><strong>❌ Missing:</strong> ${data.missing_aspects.join(', ')}</p>` : ''}
            `;
        case 'hallucination':
            return `
                <p><strong>Detected:</strong> ${data.hallucination_detected ? '⚠️ YES' : '✅ NO'}</p>
                <p><strong>Score:</strong> ${(data.hallucination_score || 0).toFixed(2)}</p>
                <p><strong>Summary:</strong> ${data.summary || 'N/A'}</p>
                ${data.hallucinated_statements?.length ? `<p><strong>🚨 Hallucinated:</strong> ${data.hallucinated_statements.map(h => h.statement).join(', ')}</p>` : ''}
            `;
        default:
            return '<p>No details available</p>';
    }
}

function renderBatchResults(results) {
    const container = document.getElementById('batchResults');
    if (!container) return;
    
    container.classList.remove('hidden');
    
    const summaryContainer = document.getElementById('batchSummary');
    const total = results.length;
    const passCount = results.filter(r => r.verdict === 'PASS').length;
    const failCount = results.filter(r => r.verdict === 'FAIL' || r.verdict === 'ERROR').length;
    const needsImprovement = results.filter(r => r.verdict === 'NEEDS IMPROVEMENT').length;
    
    const avgRelevance = results.reduce((s, r) => s + parseFloat(r.relevance), 0) / total || 0;
    const avgAccuracy = results.reduce((s, r) => s + parseFloat(r.accuracy), 0) / total || 0;
    const avgCompleteness = results.reduce((s, r) => s + parseFloat(r.completeness), 0) / total || 0;
    const avgHallucination = results.reduce((s, r) => s + parseFloat(r.hallucination), 0) / total || 0;
    
    if (summaryContainer) {
        summaryContainer.innerHTML = `
            <div class="summary-item"><div class="label">Total</div><div class="value">${total}</div></div>
            <div class="summary-item"><div class="label">✅ Pass</div><div class="value" style="color:#4ade80;">${passCount}</div></div>
            <div class="summary-item"><div class="label">⚠️ Needs Improvement</div><div class="value" style="color:#fbbf24;">${needsImprovement}</div></div>
            <div class="summary-item"><div class="label">❌ Fail</div><div class="value" style="color:#f87171;">${failCount}</div></div>
            <div class="summary-item"><div class="label">📊 Avg Relevance</div><div class="value">${avgRelevance.toFixed(2)}</div></div>
            <div class="summary-item"><div class="label">🎯 Avg Accuracy</div><div class="value">${avgAccuracy.toFixed(2)}</div></div>
            <div class="summary-item"><div class="label">📋 Avg Completeness</div><div class="value">${avgCompleteness.toFixed(2)}</div></div>
            <div class="summary-item"><div class="label">🚨 Avg Hallucination</div><div class="value">${avgHallucination.toFixed(2)}</div></div>
        `;
    }
    
    const tableContainer = document.getElementById('batchTable');
    if (tableContainer) {
        tableContainer.innerHTML = `
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Question</th>
                            <th>Relevance</th>
                            <th>Accuracy</th>
                            <th>Completeness</th>
                            <th>Hallucination</th>
                            <th>Verdict</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map((r, i) => `
                            <tr>
                                <td>${i+1}</td>
                                <td>${r.question}</td>
                                <td>${r.relevance}</td>
                                <td>${r.accuracy}</td>
                                <td>${r.completeness}</td>
                                <td>${r.hallucination}</td>
                                <td style="color: ${r.verdict === 'PASS' ? '#4ade80' : r.verdict === 'FAIL' ? '#f87171' : '#fbbf24'}">${r.verdict}</td>
                                <td>${r.status}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    const downloadBtn = document.getElementById('downloadCsvBtn');
    if (downloadBtn) {
        downloadBtn.onclick = () => {
            const headers = ['Question', 'Relevance', 'Accuracy', 'Completeness', 'Hallucination', 'Verdict', 'Status'];
            const rows = results.map(r => [
                `"${r.question}"`,
                r.relevance,
                r.accuracy,
                r.completeness,
                r.hallucination,
                r.verdict,
                r.status
            ]);
            const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `batch_results_${new Date().toISOString().slice(0,10)}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        };
    }
}

function renderDashboardStats(stats) {
    const container = document.getElementById('dashboardStats');
    if (!container) return;
    
    const items = [
        { label: 'Total Evaluations', value: stats.total || 42 },
        { label: 'Pass Rate', value: stats.passRate || '87%' },
        { label: 'Avg Relevance', value: stats.avgRelevance || '8.5' },
        { label: 'Hallucination Rate', value: stats.hallucinationRate || '13%' }
    ];
    
    container.innerHTML = items.map(item => `
        <div class="dashboard-stat">
            <div class="value">${item.value}</div>
            <div class="label">${item.label}</div>
        </div>
    `).join('');
}