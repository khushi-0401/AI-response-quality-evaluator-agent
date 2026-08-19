// =============================================
// PDF REPORT GENERATOR - VeriScore AI
// Development of AI Response Validation System
// with Hallucination Detection Assistance
// =============================================

function generatePDFReport(results, summary) {
    // Build the report HTML
    const reportHTML = buildReportHTML(results, summary);
    
    // Open in new window for printing as PDF
    const win = window.open('', '_blank', 'width=1000,height=800');
    if (!win) {
        alert('Please allow popups to generate the report.');
        return;
    }
    
    win.document.write(reportHTML);
    win.document.close();
    win.focus();
    
    // Auto-print after 1 second
    setTimeout(() => {
        win.print();
    }, 1000);
}

function buildReportHTML(results, summary) {
    const now = new Date();
    const dateStr = now.toLocaleDateString();
    const timeStr = now.toLocaleTimeString();
    
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <title>VeriScore AI - Evaluation Report</title>
        <style>
            /* ============================================= */
            /* REPORT STYLES */
            /* ============================================= */
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 30px;
                max-width: 1100px;
                margin: 0 auto;
                background: #ffffff;
                color: #1a1a2e;
            }
            .report-header {
                border-bottom: 3px solid #667eea;
                padding-bottom: 15px;
                margin-bottom: 25px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
            }
            .report-header h1 {
                color: #667eea;
                font-size: 28px;
                font-weight: 700;
            }
            .report-header .subtitle {
                color: #888;
                font-size: 14px;
            }
            .report-header .date {
                color: #888;
                font-size: 14px;
                text-align: right;
            }
            .section {
                margin-bottom: 25px;
            }
            .section-title {
                font-size: 18px;
                font-weight: 600;
                color: #302b63;
                border-bottom: 2px solid #e0e0e0;
                padding-bottom: 8px;
                margin-bottom: 15px;
            }
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-bottom: 20px;
            }
            .summary-card {
                background: #f5f7fa;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                border-left: 4px solid #667eea;
            }
            .summary-card .value {
                font-size: 28px;
                font-weight: 700;
                color: #1a1a2e;
            }
            .summary-card .label {
                font-size: 12px;
                color: #888;
                margin-top: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .summary-card.pass { border-left-color: #4ade80; }
            .summary-card.improve { border-left-color: #fbbf24; }
            .summary-card.fail { border-left-color: #f87171; }
            .summary-card.avg { border-left-color: #667eea; }
            
            .scores-grid {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 10px;
                margin: 15px 0 20px 0;
            }
            .score-item {
                background: #f5f7fa;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
            }
            .score-item .label { font-size: 11px; color: #888; text-transform: uppercase; }
            .score-item .value { font-size: 22px; font-weight: 700; color: #1a1a2e; }
            
            table {
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
                margin: 15px 0;
            }
            th {
                background: #667eea;
                color: white;
                padding: 10px 12px;
                text-align: left;
                font-weight: 600;
            }
            td {
                padding: 10px 12px;
                border-bottom: 1px solid #e8e8e8;
            }
            tr:nth-child(even) { background: #f8f9fa; }
            tr:hover { background: #edf2f7; }
            .verdict-pass { color: #22c55e; font-weight: 600; }
            .verdict-fail { color: #ef4444; font-weight: 600; }
            .verdict-improve { color: #f59e0b; font-weight: 600; }
            
            .recommendations {
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px 20px;
                border-radius: 8px;
                margin-top: 15px;
            }
            .recommendations ul {
                margin: 10px 0 0 20px;
            }
            .recommendations li {
                margin: 5px 0;
                color: #78350f;
            }
            .footer {
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #ddd;
                text-align: center;
                color: #aaa;
                font-size: 12px;
            }
            .print-btn {
                display: inline-block;
                padding: 10px 30px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                margin: 15px 0;
            }
            .print-btn:hover { background: #5a6fd6; }
            @media print {
                .no-print { display: none; }
                body { padding: 15px; }
                .summary-card { background: #f0f0f0; }
                .score-item { background: #f0f0f0; }
                .recommendations { background: #fef3c7; }
                tr:nth-child(even) { background: #f5f5f5; }
            }
            @media (max-width: 768px) {
                .summary-grid { grid-template-columns: 1fr 1fr; }
                .scores-grid { grid-template-columns: 1fr 1fr; }
                table { font-size: 11px; }
                th, td { padding: 6px 8px; }
            }
        </style>
    </head>
    <body>
        <!-- ============================================= -->
        <!-- HEADER -->
        <!-- ============================================= -->
        <div class="report-header">
            <div>
                <h1>📊 VeriScore AI</h1>
                <div class="subtitle">AI Response Validation System with Hallucination Detection Assistance</div>
            </div>
            <div class="date">
                <div><strong>Report Date:</strong> ${dateStr}</div>
                <div><strong>Time:</strong> ${timeStr}</div>
                <div><strong>Total Evaluations:</strong> ${results.length}</div>
            </div>
        </div>

        <!-- ============================================= -->
        <!-- SUMMARY -->
        <!-- ============================================= -->
        <div class="section">
            <div class="section-title">📈 Summary</div>
            <div class="summary-grid">
                <div class="summary-card pass">
                    <div class="value">${summary.pass}</div>
                    <div class="label">✅ Pass</div>
                </div>
                <div class="summary-card improve">
                    <div class="value">${summary.needsImprovement}</div>
                    <div class="label">⚠️ Needs Improvement</div>
                </div>
                <div class="summary-card fail">
                    <div class="value">${summary.fail}</div>
                    <div class="label">❌ Fail</div>
                </div>
                <div class="summary-card avg">
                    <div class="value">${summary.passRate}%</div>
                    <div class="label">📊 Pass Rate</div>
                </div>
            </div>
        </div>

        <!-- ============================================= -->
        <!-- AVERAGE SCORES -->
        <!-- ============================================= -->
        <div class="section">
            <div class="section-title">📊 Average Scores</div>
            <div class="scores-grid">
                <div class="score-item">
                    <div class="label">Relevance</div>
                    <div class="value">${summary.avgRelevance}</div>
                </div>
                <div class="score-item">
                    <div class="label">Accuracy</div>
                    <div class="value">${summary.avgAccuracy}</div>
                </div>
                <div class="score-item">
                    <div class="label">Completeness</div>
                    <div class="value">${summary.avgCompleteness}</div>
                </div>
                <div class="score-item" style="border-bottom: 3px solid #fc8181;">
                    <div class="label">Hallucination</div>
                    <div class="value">${summary.avgHallucination}</div>
                </div>
                <div class="score-item" style="border-bottom: 3px solid #667eea;">
                    <div class="label">Overall</div>
                    <div class="value">${summary.avgOverall}</div>
                </div>
            </div>
        </div>

        <!-- ============================================= -->
        <!-- DETAILED RESULTS -->
        <!-- ============================================= -->
        <div class="section">
            <div class="section-title">📋 Detailed Results</div>
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
                    </tr>
                </thead>
                <tbody>
                    ${results.map((r, i) => `
                        <tr>
                            <td>${i+1}</td>
                            <td>${r.question.replace(/"/g, '&quot;')}</td>
                            <td>${r.relevance}</td>
                            <td>${r.accuracy}</td>
                            <td>${r.completeness}</td>
                            <td>${r.hallucination}</td>
                            <td class="verdict-${r.verdict.toLowerCase().replace(' ', '')}">${r.verdict}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>

        <!-- ============================================= -->
        <!-- RECOMMENDATIONS -->
        <!-- ============================================= -->
        <div class="section">
            <div class="section-title">🔍 Improvement Recommendations</div>
            <div class="recommendations">
                <ul>
                    <li><strong>Accuracy:</strong> Average score is ${summary.avgAccuracy}. Focus on improving factual correctness by using more reference data.</li>
                    <li><strong>Hallucination:</strong> ${summary.hallucinationRate}% of evaluations had hallucinations. Improve RAG grounding with better source context.</li>
                    <li><strong>Completeness:</strong> Average score is ${summary.avgCompleteness}. Ensure responses cover all aspects of the question.</li>
                    <li><strong>Pass Rate:</strong> ${summary.passRate}% of evaluations passed. Review failed cases for common patterns.</li>
                    <li><strong>Recommendation:</strong> Consider adding more training data and refining the RAG knowledge base.</li>
                </ul>
            </div>
        </div>

        <!-- ============================================= -->
        <!-- FOOTER -->
        <!-- ============================================= -->
        <div class="footer">
            <p>Report generated by VeriScore AI · Powered by Google Gemini</p>
            <p>© ${new Date().getFullYear()} AI Response Validation System</p>
        </div>

        <!-- ============================================= -->
        <!-- PRINT BUTTON -->
        <!-- ============================================= -->
        <div class="no-print" style="text-align:center; margin-top:20px;">
            <button class="print-btn" onclick="window.print()">🖨️ Save as PDF / Print</button>
            <br>
            <small style="color:#888;">Click the button above and select "Save as PDF" in the print dialog.</small>
        </div>
    </body>
    </html>
    `;
}