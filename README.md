# 🕵 LLM Response Evaluation Pipeline

**Author:** Sail Nagale  
**Assignment:** BeyondChats LLM Engineer Internship

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
# Install dependencies
pip install openai tiktoken
