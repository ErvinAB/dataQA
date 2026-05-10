import pandas as pd
from typing import Dict, Any, List
import numpy as np
from src.utils.logger import setup_logger
try:
    from scipy import stats
except ImportError:
    stats = None

logger = setup_logger("drift_detector")

class DataDriftException(Exception):
    """Raised when severe data drift is detected in the pipeline."""
    pass

class DataDriftDetector:
    """
    Detects statistical data drift between a reference dataset (e.g., training data)
    and an incoming dataset (e.g., current production batch).
    """

    def __init__(self, p_value_threshold: float = 0.05, enforce_failure: bool = True):
        self.p_value_threshold = p_value_threshold
        self.enforce_failure = enforce_failure
        if stats is None:
            logger.warning("scipy is not installed. Drift detection will return mocked results. Please install scipy for real statistical tests.")

    def detect_drift(self, reference_df: pd.DataFrame, current_df: pd.DataFrame, numerical_columns: List[str]) -> Dict[str, Any]:
        """
        Uses the Kolmogorov-Smirnov (K-S) test to detect if two continuous distributions differ significantly.
        """
        logger.info(f"Running Data Drift Detection on {len(numerical_columns)} columns...")
        
        results = {
            "drift_detected": False,
            "columns_with_drift": [],
            "details": {}
        }

        for col in numerical_columns:
            if col not in reference_df.columns or col not in current_df.columns:
                logger.warning(f"Column '{col}' missing from one of the dataframes. Skipping.")
                continue

            ref_data = reference_df[col].dropna()
            cur_data = current_df[col].dropna()

            if ref_data.empty or cur_data.empty:
                continue

            if stats:
                # Run two-sample K-S test
                ks_stat, p_value = stats.ks_2samp(ref_data, cur_data)
                is_drifted = p_value < self.p_value_threshold
            else:
                # Mock logic if scipy is missing
                mean_diff = abs(ref_data.mean() - cur_data.mean())
                std_pool = np.sqrt((ref_data.var() + cur_data.var()) / 2)
                # If mean shifted by more than 1 standard deviation, mock it as drift
                is_drifted = mean_diff > std_pool
                p_value = 0.01 if is_drifted else 0.5
                ks_stat = 0.5 if is_drifted else 0.1

            results["details"][col] = {
                "p_value": float(p_value),
                "ks_stat": float(ks_stat),
                "drift_detected": bool(is_drifted)
            }

            if is_drifted:
                results["columns_with_drift"].append(col)
                results["drift_detected"] = True

        if results["drift_detected"]:
            error_msg = f"Data Drift detected in columns: {results['columns_with_drift']}"
            logger.error(error_msg)
            if self.enforce_failure:
                raise DataDriftException(f"Pipeline halted to prevent model degradation: {error_msg}")
        else:
            logger.info("No significant data drift detected.")

        return results

