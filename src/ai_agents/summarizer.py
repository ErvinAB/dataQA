import json
import urllib.request
import urllib.error
from typing import List, Dict, Any
from src.utils.logger import setup_logger

logger = setup_logger("ai_summarizer")

class AIFailureSummarizer:
    """
    AI Agent that summarizes data quality validation failures.
    Simulates sending data to an LLM provider (e.g., OpenAI API) by
    using a mock REST API endpoint to demonstrate cloud integrations.
    """
    
    def __init__(self, endpoint: str = "https://jsonplaceholder.typicode.com/posts"):
        self.endpoint = endpoint
        logger.info(f"Initialized AI Summarizer Agent pointing to API: {self.endpoint}")

    def _call_llm_api(self, prompt: str) -> str:
        """Simulates an API call to an LLM provider."""
        data = json.dumps({"title": "AI RCA Request", "body": prompt, "userId": 1}).encode('utf-8')
        req = urllib.request.Request(self.endpoint, data=data, headers={'Content-Type': 'application/json'})
        
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status in (200, 201):
                    logger.info("Successfully received response from AI API.")
                    # We just pretend the API returned the actual RCA text we want
                    return "API_SUCCESS"
                else:
                    return "API_ERROR"
        except Exception as e:
            logger.warning(f"AI API call failed: {e}. Falling back to local generation.")
            return "API_ERROR"

    def generate_root_cause_analysis(self, failures: List[Dict[str, Any]]) -> str:
        """
        Analyzes a list of validation failures and returns a human-readable RCA.
        """
        if not failures:
            return "✅ **AI Analysis**: No data quality failures detected. The pipeline is healthy."

        logger.info(f"AI Agent generating prompt for {len(failures)} failures...")
        prompt = f"Analyze these failures: {json.dumps(failures)}"
        
        # Simulate the network call to the LLM
        api_status = self._call_llm_api(prompt)
        
        analysis_lines = [
            f"⚠️ **AI Root Cause Analysis Report** (API Status: `{api_status}`)",
            f"Detected **{len(failures)}** distinct data quality issue(s).",
            "",
            "**Key Findings:**"
        ]
        
        for idx, failure in enumerate(failures, 1):
            check_name = failure.get("check_name", "Unknown Check")
            message = failure.get("message", "")
            
            if "not_null" in check_name:
                rca = "Likely caused by an upstream schema change or dropped fields in the source system extraction phase."
                severity = "High"
            elif "pattern" in check_name or "accepted_values" in check_name:
                rca = "Potential UI validation bug allowing dirty input, or incorrect mapping from a third-party API."
                severity = "Medium"
            elif "cross_field" in check_name:
                rca = "Business logic violation in the source application (e.g., closing a session before it starts)."
                severity = "High"
            else:
                rca = "Data anomaly requires manual investigation."
                severity = "Low"
                
            analysis_lines.append(f"{idx}. **[{severity}] {check_name}**: {message}")
            analysis_lines.append(f"   *Suggested Root Cause*: {rca}")
            
        analysis_lines.append("")
        analysis_lines.append("**Recommended Action**: Halt downstream ETL until the source system team confirms the schema/logic fix.")
        
        return "\n".join(analysis_lines)

