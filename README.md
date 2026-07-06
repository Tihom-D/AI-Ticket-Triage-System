# AI Ticket Triage System (Dual-Agent Architecture)

An enterprise-grade, automated IT support ticket triage system powered by LLMs. This project simulates a real-world pipeline (like Salesforce/ServiceNow) where customer support tickets are automatically categorized, analyzed for sentiment, and assigned urgency.

## Key Features
* **Dual-Agent Workflow:** * **Agent 1 (Extractor):** Analyzes the raw ticket and extracts Sentiment, Urgency, Category, and a Summary.
  * **Agent 2 (Auditor):** Acts as a strict QA layer to compare Agent 1's output against the original ticket, preventing AI hallucinations.
* **Fault Tolerance:** Implements robust error handling (`try-except`), API rate-limit management (`time.sleep`), and timeout fallback mechanisms (`timeout=15`).
* **Human-in-the-Loop:** Automatically flags misclassified or ambiguous tickets for manual review (`REQUIRES HUMAN REVIEW`).

## Tech Stack
* **Language:** Python
* **Data Processing:** Pandas (for exporting clean, structured CSV reports)
* **AI Integration:** OpenRouter API (utilizing state-of-the-art free LLMs)
* **Requests:** REST API interactions

## How to Run
1. Clone this repository.
2. Get a free API key from [OpenRouter](https://openrouter.ai/).
3. Replace `"YOUR_OPENROUTER_API_KEY_HERE"` in `triage_ai.py` with your key.
4. Run the script: `python triage_ai.py`
5. Check the generated `verified_triage_report.csv` for the final audited data!
