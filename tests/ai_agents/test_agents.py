import pytest
import pandas as pd
import numpy as np
from src.ai_agents.summarizer import AIFailureSummarizer
from src.ai_agents.drift_detector import DataDriftDetector

def test_summarizer_empty():
    summarizer = AIFailureSummarizer()
    res = summarizer.generate_root_cause_analysis([])
    assert "No data quality failures detected" in res

def test_summarizer_with_failures():
    failures = [
        {"check_name": "not_null", "message": "Nulls found in id"},
        {"check_name": "cross_field", "message": "start > end"}
    ]
    summarizer = AIFailureSummarizer()
    res = summarizer.generate_root_cause_analysis(failures)
    
    assert "Detected **2** distinct data quality issue" in res
    assert "upstream schema change" in res  # Matches not_null heuristic
    assert "Business logic violation" in res # Matches cross_field heuristic

def test_drift_detector_no_drift():
    # Two identical distributions
    np.random.seed(42)
    ref_df = pd.DataFrame({"age": np.random.normal(30, 5, 100)})
    cur_df = pd.DataFrame({"age": np.random.normal(30, 5, 100)})
    
    detector = DataDriftDetector(p_value_threshold=0.01)
    res = detector.detect_drift(ref_df, cur_df, ["age"])
    
    assert res["drift_detected"] is False

def test_drift_detector_with_drift():
    # Two different distributions
    np.random.seed(42)
    ref_df = pd.DataFrame({"age": np.random.normal(30, 5, 100)})
    cur_df = pd.DataFrame({"age": np.random.normal(50, 5, 100)}) # Shifted mean
    
    detector = DataDriftDetector(p_value_threshold=0.05)
    res = detector.detect_drift(ref_df, cur_df, ["age"])
    
    assert res["drift_detected"] is True
    assert "age" in res["columns_with_drift"]
