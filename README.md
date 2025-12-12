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
## 🏗️ Architecture

The pipeline processes data through two distinct tiers to optimize for cost and accuracy.

```text
[ Raw JSON Inputs ]
       |
       v
[ 1. Data Parsing Module ] 
       |
       +-------------------------------------+
       |                                     |
[ 2. Deterministic Layer ]          [ 3. Semantic Layer ]
(Python + Tiktoken)                 (OpenAI GPT-3.5 Judge)
       |                                     |
       |-- Calculate Tokens                  |-- Check Hallucinations
       |-- Estimate Costs                    |-- Verify Relevance
       |                                     |
       +------------------+------------------+
                          |
                          v
                [ 4. Aggregation ]
                          |
                          v
             [ FINAL EVALUATION REPORT ]
```
## 🧠 Design Decisions
LLM-as-a-Judge: Replaced rigid text-match metrics (BLEU/ROUGE) with semantic evaluation to accurately distinguish between valid answers and hallucinations.

Chain-of-Thought (CoT): Implemented reasoning-first prompting (reason before score) to significantly reduce false positive grades.

Proactive Costing: Integrated tiktoken for local cost estimation before API calls, enabling budget caps and proactive filtering.

Context-Aware Logic: Replaced "brute force" looping with smart parsing that isolates valid User→AI turns, preventing wasteful evaluation of system prompts or simple chit-chat.

## 🚀 Scalability Strategy (Millions of Users)
To ensure minimal latency and cost at scale:

Async Decoupling: Evaluation is offloaded to background workers via message queues (Kafka/RabbitMQ), ensuring zero impact on user-facing chat latency.

Tiered Sampling:

Tier 1 (100%): Free, deterministic metrics (Cost/Latency) run on every chat.

Tier 2 (5%): Expensive LLM grading runs only on a statistical sample.

Tier 3 (Priority): Immediate evaluation triggered only by negative user feedback (e.g., "thumbs down").

Model Distillation: Replace general-purpose models (GPT-4) with specialized, small models (e.g., Llama-3-8B or GPT-4o-mini) to reduce inference costs by ~90%.
