# 🕵️‍♂️ LLM Response Evaluation Pipeline

**Author:** Sail Nagale
**Assignment:** BeyondChats LLM Engineer Internship

## ⚠️ Note on API Usage (Mock Mode)

To ensure this submission runs successfully on any machine without requiring immediate access to a paid OpenAI API key, I have implemented a **Mock Mode** flag in the code.

* **Default Behavior:** `MOCK_MODE = True`. The script simulates LLM responses (returning mock scores and reasoning) to demonstrate the pipeline's architecture, data parsing, and reporting logic without incurring costs.
* **Production Behavior:** To run with a real LLM, simply set `MOCK_MODE = False` in `main.py` and export your `OPENAI_API_KEY`.

This design pattern ensures the evaluation pipeline is testable and robust even in environments where external APIs are restricted or unavailable.

---

## 📋 Project Overview

This project acts as an automated "Quality Assurance Supervisor" for RAG-based chatbots. It ingests conversation logs and context vectors to evaluate AI performance across three critical dimensions:

1.  **Relevance:** Did the AI answer the user's specific intent? (Semantic Analysis)
2.  **Factual Accuracy:** Did the AI hallucinate facts not present in the source context? (RAG Verification)
3.  **Operational Metrics:** Token usage, estimated cost, and response latency.

---

## ⚙️ Local Setup Instructions

Follow these steps to run the pipeline on your local machine.

### 1. Prerequisites
* Python 3.10 or higher
* `pip` (Python package installer)

### 2. Installation
Clone the repository and install the required dependencies:

```bash
pip install openai tiktoken
```

Architecture
The pipeline follows a Tiered Evaluation Architecture designed to balance accuracy with cost.

Code snippet

graph TD
    A[Input JSONs] --> B[Data Parser]
    B --> C{Evaluation Engine}
    C -->|Tier 1: Deterministic| D[Cost & Token Calculator]
    D -->|Tiktoken| E[Cost Metrics]
    C -->|Tier 2: Semantic| F[LLM-as-a-Judge]
    F -->|Prompt: Hallucination Check| G[Factual Score]
    F -->|Prompt: Relevance Check| H[Relevance Score]
    E --> I[Aggregator]
    G --> I
    H --> I
    I --> J[Final JSON Report]
