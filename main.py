"""
Project: LLM Response Evaluation Pipeline
Assignment: BeyondChats LLM Engineer Internship
Author: Sail Nagale
Date: December 12, 2025

Description:
This script evaluates RAG chatbot responses based on:
1. Relevance (LLM-as-a-Judge)
2. Factual Accuracy (Hallucination Detection)
3. Latency & Cost Metrics

"""


import json
import time
import os
import random
import tiktoken
 
# here i am using try-block in case the user doesn't have the lib installed.
try:
    from openai import OpenAI, APIConnectionError, RateLimitError
except ImportError:
    OpenAI = None


CHAT_DATA_PATH = 'sample-chat-conversation-01.json'
CONTEXT_DATA_PATH = 'sample_context_vectors-01.json'
REPORT_OUTPUT_PATH = 'evaluation_report.json'

#for testing i am using mock mode to save api credits
MOCK_MODE = True 


#if using api
if not MOCK_MODE:
    client = OpenAI() 
else:
    client = None
    print("\n RUNNING IN MOCK MODE (No API)\n")
    print("The pipeline will simulate LLM responses for demonstration purposes.\n")


# EVALUATION LOGIC

class EvaluationPipeline:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        
        # using Tiktoken for calculating costs locally
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            
        self.input_cost_per_1k = 0.0005 
        self.output_cost_per_1k = 0.0015

    def get_token_count(self, text):
        if not text: return 0
        return len(self.tokenizer.encode(text))
# here I have implemented token counting to estimate production costs accurately ($0.001 per run).
    def calculate_costs(self, input_text, output_text):
        """
        Calculates deterministic cost metrics. 
        (This works for real even in Mock Mode!)
        """
        in_tokens = self.get_token_count(input_text)
        out_tokens = self.get_token_count(output_text)
        
        total_cost = ((in_tokens / 1000) * self.input_cost_per_1k) + \
                     ((out_tokens / 1000) * self.output_cost_per_1k)
        
        return {
            "tokens_input": in_tokens,
            "tokens_output": out_tokens,
            "estimated_cost_usd": round(total_cost, 6)
        }

    def _simulate_llm_response(self, system_prompt):
      
        # Adding a tiny fake delay only for simulation
        time.sleep(0.1) 
        
        # Logic: Randomly succeed or fail to show diversity in the report
        is_pass = random.choice([True, True, True, False]) # 75% pass rate
        
        if "hallucination" in system_prompt.lower():
            if is_pass:
                return {"score": 1, "reason": "[Mock] The answer is fully supported by the provided context text."}
            else:
                return {"score": 0, "reason": "[Mock] The answer mentions '2025', but the context only contains data up to '2024'."}
        else:
            # Relevance check
            if is_pass:
                return {"score": 1, "reason": "[Mock] The answer directly addresses the user's question about IVF costs."}
            else:
                return {"score": 0, "reason": "[Mock] The user asked for a location, but the AI provided a phone number."}

    def safe_api_call(self, system_prompt, user_prompt, max_retries=3):
        
        if MOCK_MODE:
            return self._simulate_llm_response(system_prompt)

        # if we use real api
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"   [Error] API call failed: {e}")
                time.sleep(1)
                
        return {"score": 0, "reason": "API Failed"}

    def check_hallucination(self, context, ai_answer):
        system_prompt = (
            "You are a strict fact-checker. \n"
            "Rules:\n"
            "1. If Answer has facts NOT in Context -> Score 0.\n"
            "2. If Answer is supported -> Score 1.\n"
            "3. Output JSON: {'reason': '...', 'score': 0 or 1}."
        )
        user_prompt = f"Context: {context[:15000]}\n\nAI Answer: {ai_answer}"
        return self.safe_api_call(system_prompt, user_prompt)

    def check_relevance(self, user_query, ai_answer):
        system_prompt = (
            "You are a response quality evaluator. \n"
            "Rules:\n"
            "1. If AI dodges question -> Score 0.\n"
            "2. If AI answers clearly -> Score 1.\n"
            "3. Output JSON: {'reason': '...', 'score': 0 or 1}."
        )
        user_prompt = f"User Query: {user_query}\n\nAI Answer: {ai_answer}"
        return self.safe_api_call(system_prompt, user_prompt)

#loading data
def load_and_parse_data():
    print("Loading data files...")
    try:
        with open(CHAT_DATA_PATH, 'r') as f:
            chat_data = json.load(f)
        with open(CONTEXT_DATA_PATH, 'r') as f:
            context_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Ensure '{CHAT_DATA_PATH}' and '{CONTEXT_DATA_PATH}' are in this folder.")
        return None, None

    pairs = []
    turns = chat_data.get('conversation_turns', [])
    for i in range(len(turns) - 1):
        if turns[i]['role'] == 'User' and turns[i+1]['role'] == 'AI/Chatbot':
            pairs.append({
                'turn_id': turns[i].get('turn', i),
                'question': turns[i]['message'],
                'answer': turns[i+1]['message']
            })

    vectors = context_data.get('data', {}).get('vector_data', [])
    full_context = "\n\n".join([v.get('text', '') for v in vectors if v.get('text')])

    return pairs, full_context


def main():
    pairs, knowledge_base = load_and_parse_data()
    if not pairs: return

    pipeline = EvaluationPipeline()
    results = []
    
    print(f"Starting evaluation on {len(pairs)} turns...")
    print("-" * 60)

    total_cost, total_rel, total_fac = 0, 0, 0

    for pair in pairs:
        print(f"Processing Turn {pair['turn_id']}...", end=" ", flush=True)
        
        # These will be simulated if MOCK_MODE is True
        cost_metrics = pipeline.calculate_costs(pair['question'], pair['answer'])
        hallucination_res = pipeline.check_hallucination(knowledge_base, pair['answer'])
        relevance_res = pipeline.check_relevance(pair['question'], pair['answer'])

        total_cost += cost_metrics['estimated_cost_usd']
        total_rel += relevance_res.get('score', 0)
        total_fac += hallucination_res.get('score', 0)

        results.append({
            "turn_id": pair['turn_id'],
            "metrics": {
                "cost": cost_metrics,
                "factual": hallucination_res,
                "relevance": relevance_res
            }
        })
        print(f"[Done] (R: {relevance_res.get('score')}, F: {hallucination_res.get('score')})")

    with open(REPORT_OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=4)

    print("\n" + "="*50)
    print("           EVALUATION SUMMARY")
    print("="*50)
    print(f"Mode Used             : {'MOCK (Simulation)' if MOCK_MODE else 'REAL API'}")
    print(f"Total Cost (Est)      : ${total_cost:.5f}")
    print(f"Avg Relevance         : {(total_rel/len(pairs))*100:.1f}%")
    print(f"Avg Factual Accuracy  : {(total_fac/len(pairs))*100:.1f}%")
    print("="*50)
    print(f"Report saved to: {REPORT_OUTPUT_PATH}")

if __name__ == "__main__":
    main()