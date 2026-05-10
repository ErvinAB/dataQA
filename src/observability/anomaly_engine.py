import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.utils.logger import setup_logger

logger = setup_logger("anomaly_engine")

class AnomalyEngine:
    """
    Detects volume anomalies or statistical outliers in incoming data.
    """
    def __init__(self, z_threshold: float = 3.0):
        self.z_threshold = z_threshold

    def detect_volume_anomaly(self, current_row_count: int, historical_counts: List[int]) -> Dict[str, Any]:
        """
        Detects if the current row count is an anomaly based on historical counts.
        """
        if not historical_counts or len(historical_counts) < 3:
            logger.info("Not enough history for volume anomaly detection.")
            return {"is_anomaly": False, "reason": "Not enough history"}
            
        mean = np.mean(historical_counts)
        std = np.std(historical_counts)
        
        if std == 0:
            std = 1.0 # Prevent division by zero if all history is identical
            
        z_score = (current_row_count - mean) / std
        is_anomaly = abs(z_score) > self.z_threshold
        
        result = {
            "is_anomaly": bool(is_anomaly),
            "current_count": current_row_count,
            "mean": float(mean),
            "z_score": float(z_score),
            "threshold": self.z_threshold
        }
        
        if is_anomaly:
            logger.warning(f"Volume Anomaly Detected! Z-score: {z_score:.2f} (Threshold: {self.z_threshold})")
        
        return result
