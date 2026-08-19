// =============================================
// API CONFIGURATION - VeriScore AI
// =============================================

const API_URL = 'http://localhost:8000';

// =============================================
// HEALTH CHECK
// =============================================

async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            return { status: 'online', data: await response.json() };
        }
        return { status: 'offline' };
    } catch (error) {
        return { status: 'offline', error: error.message };
    }
}

// =============================================
// EVALUATE ALL AGENTS
// =============================================

async function evaluateAll(payload) {
    const response = await fetch(`${API_URL}/api/agents/evaluate-all`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
        const error = await response.text();
        throw new Error(`API Error: ${error}`);
    }
    
    return await response.json();
}

// =============================================
// GET SUBMISSION STATUS
// =============================================

async function getSubmissionStatus(submissionId) {
    const response = await fetch(`${API_URL}/api/evaluations/${submissionId}`);
    if (!response.ok) {
        throw new Error('Failed to fetch submission');
    }
    return await response.json();
}

// =============================================
// GET STATS FOR SIDEBAR & DASHBOARD
// =============================================

async function getStats() {
    try {
        const response = await fetch(`${API_URL}/api/stats`);
        if (!response.ok) {
            throw new Error('Failed to fetch stats');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching stats:', error);
        return null;
    }
}

// =============================================
// SINGLE EVALUATION
// =============================================

async function submitSingleEvaluation(payload) {
    const response = await fetch(`${API_URL}/api/evaluations/single`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
        const error = await response.text();
        throw new Error(`API Error: ${error}`);
    }
    
    return await response.json();
}

// =============================================
// RAG STATUS
// =============================================

async function getRagStatus() {
    try {
        const response = await fetch(`${API_URL}/api/rag/status`);
        if (!response.ok) {
            throw new Error('Failed to fetch RAG status');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching RAG status:', error);
        return null;
    }
}