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
## Design Decisions: Why this way?
1. Why "LLM-as-a-Judge"?
Traditional metrics like BLEU or ROUGE are insufficient for chatbots because they rely on exact word overlap. A chatbot can give a correct answer using completely different words than the reference. I chose an LLM-based evaluator because it captures semantic meaning, allowing it to distinguish between a "polite refusal" (valid) and a "hallucination" (invalid).

2. Why Chain-of-Thought Prompting?
In the evaluation prompts, I force the model to output a reason before the score.

Without CoT: The model often guesses "1" or "0" arbitrarily.

With CoT: Forcing the model to explain why ("The context mentions 2024, but the answer says 2025") significantly reduces false positives.

3. Why tiktoken for Costs?
API costs are non-trivial at scale. Relying on the API response for usage data is reactive. By using tiktoken locally, we can estimate (and potentially cap) costs before sending the request, adding a layer of budget safety.

4. Logic vs. Brute Force: The "Smart" Approach
A basic "brute-force" approach would simply loop through every single conversation turn and feed it into GPT-4. While simple to write, this approach is production-hostile because:

It burns money: Grading simple greetings (e.g., "Hi", "Thanks") costs the same as grading complex queries.

It adds latency: Blocking the pipeline for every message slows down throughput.

My Optimized Approach: Instead of blind evaluation, this pipeline implements Context-Aware Parsing:

Pairing Logic: The script specifically identifies User -> AI turn pairs. It doesn't waste tokens evaluating the AI talking to itself or system messages.

Deterministic First: We calculate "Free" metrics (Costs/Tokens) locally using tiktoken before making any API calls. This allows us to filter or cap requests if they exceed budget thresholds before they even reach the LLM.

Simulation Capability: The MOCK_MODE isn't just for testing; it demonstrates an architecture where we can swap the "Real Judge" for a "Heuristic Judge" (e.g., regex checks) for lower-priority conversations, preventing the "brute force" waste of resources.

## Scalability Strategy
Addressing the requirement: "How to ensure latency and costs remain minimum at scale (millions of conversations)?"

Running a GPT-4 evaluation on every single message in real-time is not viable for millions of users. Here is the production strategy:

1. Asynchronous Processing (Latency Optimization)
Evaluation must never block the user experience.

Strategy: Decouple evaluation from the chat loop. Push conversation logs to a high-throughput message queue (e.g., Kafka or RabbitMQ).

Implementation: A separate fleet of "Worker" services consumes these logs and runs this Python script in the background, ensuring user latency remains at milliseconds.

2. Tiered Sampling (Cost Optimization)
We do not need to evaluate 100% of conversations with an expensive LLM.

Tier 1 (100% of Traffic): Run the Deterministic Metrics (Cost/Latency) on everything. It is computationally free.

Tier 2 (Statistical Sampling): Run the LLM Judge on a random 5% sample of traffic.

Tier 3 (Trigger-Based): Immediately evaluate any conversation where the user signals dissatisfaction (e.g., "thumbs down" or negative sentiment detected).

3. Model Distillation
For the "Judge" model, we would move away from general-purpose models like GPT-4.

Strategy: Fine-tune a smaller, cheaper model (like Llama-3-8B or GPT-4o-mini) specifically on the task of "Hallucination Detection."

Impact: This reduces inference costs by ~10x-20x while maintaining high accuracy for this specific binary classification task.
