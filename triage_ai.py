import json
import requests
import pandas as pd
import time

OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY_HERE"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Mock Data: Simulating incoming support tickets from Salesforce/ServiceNow REST API
tickets = [
    {"ticket_id": "TCK-001", "customer": "Acme Corp", "description": "The billing portal is down again! We are losing money every minute. Fix this ASAP!"},
    {"ticket_id": "TCK-002", "customer": "Stark Ind", "description": "How do I change my profile picture? The current UI is a bit confusing."},
    {"ticket_id": "TCK-003", "customer": "Wayne Ent", "description": "We paid our invoice twice by mistake. Need a refund processed, this is very frustrating."},
]

# --- AGENT 1: THE EXTRACTOR (Primary Data Analysis) ---
def analyze_ticket_with_ai(description):
    prompt = f"""
    You are an IT Support Triage system. Analyze this ticket: "{description}"
    Output strictly as JSON:
    - "sentiment": (Angry, Happy, Neutral, Frustrated)
    - "urgency": (High, Medium, Low)
    - "category": (Billing, Tech Support, General Query)
    - "summary": (A 1-line summary)
    """
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "openrouter/free", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}

    try:
        # Added timeout=15 so it doesn't wait forever
        response = requests.post(API_URL, headers=headers, json=data, timeout=15)
        response_data = response.json()
        
        if 'choices' not in response_data:
            print(f"\n❌ OPENROUTER AGENT 1 ERROR: {response_data}\n")
            return {"sentiment": "Unknown", "urgency": "Unknown", "category": "Unknown", "summary": "API Error"}
            
        return json.loads(response_data['choices'][0]['message']['content'])
    except Exception as e:
        print(f"\n⏳ AGENT 1 TIMEOUT/ERROR: {str(e)}\n")
        return {"sentiment": "Unknown", "urgency": "Unknown", "category": "Unknown", "summary": f"System Error"}

# --- AGENT 2: THE AUDITOR (Hallucination Validation Layer) ---
def validate_ai_output(original_text, ai_output):
    prompt = f"""
    You are a strict QA Auditor. 
    Original Customer Ticket: "{original_text}"
    AI Generated Output: {json.dumps(ai_output)}
    
    Task: Does the AI output accurately reflect the original ticket? Did it hallucinate or misclassify the category or urgency?
    Output strictly as JSON:
    - "is_valid": (true or false)
    - "audit_reason": (1 line explaining why it passed or failed)
    """
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "openrouter/free", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}

    try:
        # Added timeout=15 so it doesn't wait forever
        response = requests.post(API_URL, headers=headers, json=data, timeout=15)
        response_data = response.json()
        
        if 'choices' not in response_data:
            print(f"\n❌ OPENROUTER AGENT 2 ERROR: {response_data}\n")
            return {"is_valid": False, "audit_reason": "API Error"}
            
        return json.loads(response_data['choices'][0]['message']['content'])
    except Exception as e:
        print(f"\n⏳ AGENT 2 TIMEOUT/ERROR: {str(e)}\n")
        return {"is_valid": False, "audit_reason": "Auditor Timeout"}

# --- MAIN EXECUTION PIPELINE ---
print("Initializing Advanced AI Triage with Validation Layer...\n")
final_report = []

for ticket in tickets:
    print(f"Processing Ticket ID: {ticket['ticket_id']} (Agent 1)...")
    initial_analysis = analyze_ticket_with_ai(ticket['description'])

    time.sleep(5)
    
    print(f"Auditing Ticket ID: {ticket['ticket_id']} (Agent 2)...")
    audit_result = validate_ai_output(ticket['description'], initial_analysis)
    
    # Merge the original ticket data, Agent 1's analysis, and Agent 2's audit results
    combined_data = {**ticket, **initial_analysis, **audit_result}
    
    # FIX: Handling LLM String vs Boolean Bug
    is_valid_flag = combined_data.get('is_valid', True)
    
    # Agar AI ne boolean ki jagah string "false" ya "False" de diya hai, toh use catch karo
    if str(is_valid_flag).strip().lower() == 'false':
        is_valid_flag = False
        
    # Fallback mechanism: If the auditor flags an issue, escalate for manual review
    if not is_valid_flag:
        combined_data['urgency'] = "REQUIRES HUMAN REVIEW"
        print(f"   ⚠️ WARNING: Agent 2 rejected this! Flagged for Human Review.") 
        
    final_report.append(combined_data)
    time.sleep(10) # Implementing rate limiting to prevent API throttling 

# --- DATA EXPORT ---
df = pd.DataFrame(final_report)
output_filename = "verified_triage_report.csv"
df.to_csv(output_filename, index=False)

print(f"\nPipeline Execution Successful! Data saved to {output_filename}.")