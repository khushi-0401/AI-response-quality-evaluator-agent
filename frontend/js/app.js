// =============================================
// MAIN APPLICATION - VeriScore AI
// =============================================

document.addEventListener('DOMContentLoaded', function() {
    checkServerStatus();
    setupTabs();
    document.getElementById('evaluateBtn').addEventListener('click', handleEvaluate);
    document.getElementById('csvFile').addEventListener('change', handleCSVUpload);
    document.getElementById('processBatchBtn').addEventListener('click', handleBatchProcess);
    loadDashboard();
});

// =============================================
// SERVER STATUS
// =============================================

async function checkServerStatus() {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    
    try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
            dot.className = 'status-dot online';
            text.textContent = '✅ System Online · All Agents Ready';
        } else {
            dot.className = 'status-dot offline';
            text.textContent = '⚠️ Server Error';
        }
    } catch {
        dot.className = 'status-dot offline';
        text.textContent = '❌ Server Offline · Run: python -m uvicorn app.main:app --reload';
    }
}

// =============================================
// TABS
// =============================================

function setupTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            document.getElementById(`tab-${this.dataset.tab}`).classList.add('active');
        });
    });
}

// =============================================
// EVALUATE
// =============================================

async function handleEvaluate() {
    const question = document.getElementById('question').value.trim();
    const aiResponse = document.getElementById('aiResponse').value.trim();
    const referenceAnswer = document.getElementById('referenceAnswer').value.trim() || null;
    const sourceContext = document.getElementById('sourceContext').value.trim() || null;
    const useRag = document.getElementById('useRag').checked;
    
    if (!question || !aiResponse) {
        alert('Please enter both Question and AI Response');
        return;
    }
    
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const btn = document.getElementById('evaluateBtn');
    
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    btn.disabled = true;
    btn.textContent = '⏳ Evaluating...';
    
    try {
        const response = await fetch('http://localhost:8000/api/agents/evaluate-all', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question,
                ai_response: aiResponse,
                reference_answer: referenceAnswer,
                source_context: sourceContext,
                use_rag: useRag
            })
        });
        
        if (!response.ok) throw new Error('API Error');
        const result = await response.json();
        
        loading.classList.add('hidden');
        results.classList.remove('hidden');
        renderScores(result);
        
        // Update sidebar with new evaluation
        await updateSidebarAfterEvaluation();
        
    } catch (error) {
        loading.classList.add('hidden');
        alert('Error: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = '🚀 Evaluate';
    }
}

// =============================================
// UPDATE SIDEBAR AFTER EVALUATION
// =============================================

async function updateSidebarAfterEvaluation() {
    try {
        const response = await fetch('http://localhost:8000/api/stats');
        if (response.ok) {
            const data = await response.json();
            if (typeof updateSidebar === 'function') {
                updateSidebar(data);
            }
        }
    } catch (error) {
        console.error('Error updating sidebar:', error);
    }
}

// =============================================
// RENDER SCORES
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

// =============================================
// RENDER DETAILS
// =============================================

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

// =============================================
// BATCH PROCESSING
// =============================================

let uploadedData = null;
let isBatchProcessing = false;

function handleCSVUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const content = e.target.result;
            const lines = content.split('\n').filter(line => line.trim() !== '');
            
            if (lines.length < 2) {
                alert('❌ CSV file must have at least one data row.');
                return;
            }
            
            const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
            
            if (!headers.includes('question') || !headers.includes('ai_response')) {
                alert('❌ CSV must have "question" and "ai_response" columns.');
                return;
            }
            
            const data = [];
            for (let i = 1; i < lines.length; i++) {
                const values = lines[i].split(',').map(v => v.trim().replace(/^"|"$/g, ''));
                const row = {};
                headers.forEach((h, idx) => {
                    row[h] = values[idx] || '';
                });
                if (row.question && row.ai_response) {
                    data.push(row);
                }
            }
            
            if (data.length === 0) {
                alert('❌ No valid rows found. Each row needs "question" and "ai_response".');
                return;
            }
            
            uploadedData = data;
            alert(`✅ Loaded ${data.length} evaluations successfully!`);
            
            const preview = document.getElementById('batchPreview');
            if (preview) {
                preview.innerHTML = `
                    <div style="margin-top:10px; padding:10px; background:rgba(255,255,255,0.05); border-radius:8px;">
                        <p style="color:rgba(255,255,255,0.5); font-size:0.9rem;">📊 ${data.length} rows loaded. Click "Process Batch" to evaluate.</p>
                        <p style="color:rgba(255,255,255,0.3); font-size:0.8rem;">Sample: ${data[0].question.substring(0, 50)}...</p>
                    </div>
                `;
            }
            
        } catch (error) {
            alert('❌ Error parsing CSV: ' + error.message);
            console.error('CSV Parse Error:', error);
        }
    };
    reader.readAsText(file);
}

async function handleBatchProcess() {
    if (isBatchProcessing) {
        alert('⏳ Batch is already processing. Please wait.');
        return;
    }
    
    if (!uploadedData || uploadedData.length === 0) {
        alert('⚠️ Please upload a CSV file first.');
        return;
    }
    
    if (!confirm(`Process ${uploadedData.length} evaluations? This may take a few minutes.`)) {
        return;
    }
    
    isBatchProcessing = true;
    
    const loading = document.getElementById('batchLoading');
    const results = document.getElementById('batchResults');
    const processBtn = document.getElementById('processBatchBtn');
    
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    processBtn.disabled = true;
    processBtn.textContent = '⏳ Processing...';
    
    const batchResults = [];
    const statusText = document.querySelector('#batchLoading p');
    const progressBar = document.querySelector('#batchLoading .spinner');
    
    for (let i = 0; i < uploadedData.length; i++) {
        const row = uploadedData[i];
        statusText.textContent = `Processing ${i+1}/${uploadedData.length}: "${row.question.substring(0, 30)}..."`;
        
        try {
            const payload = {
                question: row.question || '',
                ai_response: row.ai_response || '',
                reference_answer: row.reference_answer || null,
                source_context: row.source_context || null,
                use_rag: false
            };
            
            const response = await fetch('http://localhost:8000/api/agents/evaluate-all', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`API Error ${response.status}: ${errorText}`);
            }
            
            const result = await response.json();
            
            batchResults.push({
                question: row.question.substring(0, 50) + (row.question.length > 50 ? '...' : ''),
                relevance: (result.relevance?.relevance_score || 0).toFixed(2),
                accuracy: (result.accuracy?.accuracy_score || 0).toFixed(2),
                completeness: (result.completeness?.completeness_score || 0).toFixed(2),
                hallucination: (result.hallucination?.hallucination_score || 0).toFixed(2),
                verdict: result.verdict?.verdict || 'N/A',
                status: result.verdict?.verdict === 'PASS' ? '✅' : '⚠️'
            });
            
        } catch (error) {
            console.error(`Error processing row ${i+1}:`, error);
            batchResults.push({
                question: (row.question || 'Unknown').substring(0, 50) + '...',
                relevance: '0.00',
                accuracy: '0.00',
                completeness: '0.00',
                hallucination: '0.00',
                verdict: 'ERROR',
                status: '❌'
            });
        }
        
        const progress = Math.round(((i + 1) / uploadedData.length) * 100);
        if (progressBar) {
            progressBar.style.width = progress + '%';
        }
    }
    
    statusText.textContent = `✅ Complete! Processed ${batchResults.length}/${uploadedData.length} evaluations.`;
    loading.classList.add('hidden');
    results.classList.remove('hidden');
    processBtn.disabled = false;
    processBtn.textContent = '🚀 Process Batch';
    isBatchProcessing = false;
    
    renderBatchResults(batchResults);
    
    // Update sidebar after batch processing
    await updateSidebarAfterEvaluation();
}

// =============================================
// RENDER BATCH RESULTS
// =============================================

function renderBatchResults(results) {
    const container = document.getElementById('batchResults');
    if (!container) return;
    
    container.classList.remove('hidden');
    
    // Summary
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
    
    // Table
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
    
    // Download button
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
    
    // Generate Report button
    const reportBtn = document.getElementById('generateReportBtn');
    if (reportBtn) {
        reportBtn.onclick = function() {
            const passCount = results.filter(r => r.verdict === 'PASS').length;
            const needsImprovementCount = results.filter(r => r.verdict === 'NEEDS IMPROVEMENT').length;
            const failCount = results.filter(r => r.verdict === 'FAIL' || r.verdict === 'ERROR').length;
            const total = results.length;
            
            const avgRelevance = (results.reduce((s, r) => s + parseFloat(r.relevance), 0) / total || 0).toFixed(2);
            const avgAccuracy = (results.reduce((s, r) => s + parseFloat(r.accuracy), 0) / total || 0).toFixed(2);
            const avgCompleteness = (results.reduce((s, r) => s + parseFloat(r.completeness), 0) / total || 0).toFixed(2);
            const avgHallucination = (results.reduce((s, r) => s + parseFloat(r.hallucination), 0) / total || 0).toFixed(2);
            const avgOverall = (results.reduce((s, r) => s + (
                parseFloat(r.relevance) + 
                parseFloat(r.accuracy) + 
                parseFloat(r.completeness) + 
                (1 - parseFloat(r.hallucination))
            ) / 4, 0) / total || 0).toFixed(2);
            
            const passRate = ((passCount / total) * 100).toFixed(1);
            const hallucinationRate = ((results.filter(r => parseFloat(r.hallucination) > 0.5).length / total) * 100 || 0).toFixed(1);
            
            const summary = {
                pass: passCount,
                needsImprovement: needsImprovementCount,
                fail: failCount,
                avgRelevance: avgRelevance,
                avgAccuracy: avgAccuracy,
                avgCompleteness: avgCompleteness,
                avgHallucination: avgHallucination,
                avgOverall: avgOverall,
                passRate: passRate,
                hallucinationRate: hallucinationRate
            };
            
            if (typeof generatePDFReport === 'function') {
                generatePDFReport(results, summary);
            } else {
                alert('Report generator not loaded. Please check if report.js is included.');
            }
        };
    }
}

// =============================================
// DASHBOARD
// =============================================

function loadDashboard() {
    const container = document.getElementById('dashboardStats');
    if (!container) return;
    
    container.innerHTML = `
        <div class="dashboard-stat"><div class="value">42</div><div class="label">Total Evaluations</div></div>
        <div class="dashboard-stat"><div class="value">87%</div><div class="label">Pass Rate</div></div>
        <div class="dashboard-stat"><div class="value">8.5</div><div class="label">Avg Relevance</div></div>
        <div class="dashboard-stat"><div class="value">13%</div><div class="label">Hallucination Rate</div></div>
    `;
}

// =============================================
// EXPOSE FUNCTIONS
// =============================================

window.updateSidebarAfterEvaluation = updateSidebarAfterEvaluation;
window.renderScores = renderScores;
window.renderDetails = renderDetails;
window.renderBatchResults = renderBatchResults;