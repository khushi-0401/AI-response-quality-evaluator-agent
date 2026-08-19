# 🤖 VeriScore AI

## AI Response Validation System with Hallucination Detection Assistance

---

## 📋 Overview

**VeriScore AI** is an AI-powered response validation system that evaluates AI-generated responses using **6 specialized agents** powered by **Google Gemini**.

It provides automatic scoring for:
- ✅ **Relevance** – Does the response answer the question?
- ✅ **Accuracy** – Is the information factually correct?
- ✅ **Completeness** – Are all aspects covered?
- ✅ **Hallucination Detection** – Are there unsupported claims?
- ✅ **Verdict** – PASS / NEEDS IMPROVEMENT / FAIL

---

## 🏗️ Project Flowchart
┌─────────────────────────────────────────────────────────────────┐
│ USER INPUT │
│ Question + AI Response + (Optional Reference) │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ RAG RETRIEVAL │
│ ChromaDB (216 documents from SQuAD + TruthfulQA) │
│ Retrieves relevant source context │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ 6 AI AGENTS (Gemini) │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│ │ Relevance │ │ Accuracy │ │ Completeness ││
│ └─────────────┘ └─────────────┘ └─────────────────────────┘│
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│ │Hallucination│ │ Verdict │ │ Validation ││
│ └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ RESULTS DISPLAY │
│ 5 Score Cards + Detailed Reasoning + Final Verdict │
└─────────────────────────────────────────────────────────────────┘

text

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI |
| **LLM** | Google Gemini 2.5 Flash |
| **Vector DB** | ChromaDB |
| **Database** | SQLite |
| **Frontend** | HTML, CSS, JavaScript |
| **Charts** | Chart.js |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 |

---

## 🚀 Installation Guide

### Prerequisites
- Python 3.11+
- Google Gemini API Key (free: https://aistudio.google.com/)

### Steps

```bash
# 1. Clone and setup
git clone <repository-url>
cd ai-evaluator-agent
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Set API key
# Create .env file with: GOOGLE_API_KEY=your-key

# 3. Build knowledge base
python build_knowledge_base.py

# 4. Start backend (Terminal 1)
python -m uvicorn app.main:app --reload

# 5. Start frontend (Terminal 2)
cd frontend
python -m http.server 3000

# 6. Open browser
http://localhost:3000