import json
from typing import List, Dict, Any
from src.utils.logger import setup_logger

logger = setup_logger("ai_summarizer")

class AIFailureSummarizer:
    """
    Mock AI Agent that summarizes data quality validation failures.
    In a real implementation, this would call an LLM (e.g., OpenAI/Anthropic)
    with a structured prompt containing the failure data.
    """
    
    def __init__(self, model: str = "mock-gemma-4"):
        self.model = model
        logger.info(f"Initialized AI Summarizer Agent with model: {self.model}")

    def generate_root_cause_analysis(self, failures: List[Dict[str, Any]]) -> str:
        """
        Analyzes a list of validation failures and returns a human-readable RCA.
        """
        if not failures:
            return "✅ **AI Analysis**: No data quality failures detected. The pipeline is healthy."

        logger.info(f"AI Agent analyzing {len(failures)} failures...")
        
        # In a real scenario, this is where you'd construct the prompt:
        # prompt = f"Analyze the following data quality failures: {json.dumps(failures)}..."
        # response = llm.generate(prompt)
        
        # --- MOCK LOGIC ---
        analysis_lines = [
            f"⚠️ **AI Root Cause Analysis Report** (Model: `{self.model}`)",
            f"Detected **{len(failures)}** distinct data quality issue(s).",
            "",
            "**Key Findings:**"
        ]
        
        for idx, failure in enumerate(failures, 1):
            check_name = failure.get("check_name", "Unknown Check")
            message = failure.get("message", "")
            
            # Simple heuristic for mock RCA
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
