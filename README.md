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
3. Usage (Mock Mode vs. Real API)
Option A: Run in Mock Mode (Default - Free) To ensure this submission is reviewable without requiring active API credits, the script defaults to MOCK_MODE = True. It simulates LLM responses to demonstrate the pipeline's logic, data parsing, and reporting capabilities.

Bash

python main.py
Option B: Run with Real OpenAI API To run the actual semantic evaluation using GPT-3.5-Turbo:

Open main.py and set MOCK_MODE = False.

Export your API key:

Bash

export OPENAI_API_KEY="sk-your-key-here"
# Or set it in your environment variables
Run the script:

Bash

python main.py
