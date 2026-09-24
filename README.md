# AI Delivery Manager

An enterprise-grade, hybrid Generative AI workforce management system. This project solves the critical failure modes of pure-LLM agents (mathematical hallucinations and black-box decision-making) by combining probabilistic natural language processing with deterministic business logic.

Built for **25ARE471: Introduction to Generative AI**.

## 🚀 Key Features

* **Hybrid Architecture:** Isolates natural language reasoning (LLM) from schedule capacity calculations (Deterministic Python). The AI reasons; the code computes.
* **LangGraph Orchestration:** Utilizes a multi-agent state graph to manage the pipeline (Parsing -> Ranking -> Reasoning).
* **Strict Schema Enforcement:** Leverages `instructor` and Pydantic to ensure 100% JSON schema adherence from local LLMs.
* **Human-in-the-Loop (HITL):** The AI operates strictly as an advisory engine. State mutations require explicit human approval via the FastAPI execution layer.
* **Bounded What-If Sandbox:** Simulates the "blast radius" of employee absences (e.g., sick leave) and recalculates workload redistribution without mutating production databases.
* **Continuous Calibration Loop:** Tracks estimated vs. actual task durations to generate personalized Employee Calibration Factors (ECF) for statistically grounded capacity forecasting.
* **Local-First Privacy:** Runs entirely offline via Ollama, ensuring zero enterprise data leakage.

## 🛠️ Tech Stack

* **Core AI:** Llama 3 (8B) via [Ollama](https://ollama.com/)
* **Orchestration:** [LangGraph](https://python.langchain.com/docs/langgraph/)
* **Structured Output:** [Instructor](https://github.com/jxnl/instructor) + Pydantic
* **Backend:** FastAPI + Python 3.12
* **Frontend:** HTML/JS + PicoCSS

## 📊 Evaluation Metrics

The system includes an automated evaluation suite (`evaluate_system.py`) to verify architectural integrity. Performance on an NVIDIA RTX 3050 Ti (16GB RAM):

| Metric | Target | Achieved Result |
| :--- | :--- | :--- |
| **Schema Adherence Rate** | >95% | **100.0%** (via Instructor retries) |
| **Deterministic Accuracy** | 100% | **100.0%** (Zero arithmetic hallucinations) |
| **Average Pipeline Latency** | <15s | **~11.4s** (End-to-End local inference) |

## ⚙️ Quick Start

### 1. Prerequisites
* Install Python 3.12+
* Install [Ollama](https://ollama.com/) and pull the Llama 3 model:
  ```bash
  ollama run llama3
