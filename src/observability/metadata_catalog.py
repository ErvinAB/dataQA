import json
import os
from datetime import datetime
from typing import Dict, Any
from src.utils.logger import setup_logger

logger = setup_logger("metadata_catalog")

class MetadataCatalog:
    """
    A lightweight JSON-based tracker for validation runs.
    Simulates an enterprise Data Catalog or metadata store.
    """
    def __init__(self, storage_path: str = "data/metadata_catalog.json"):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists(os.path.dirname(self.storage_path)):
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump([], f)

    def log_run(self, dataset_name: str, total_rows: int, failed_checks: int, passed_checks: int, ai_analysis_summary: str = ""):
        """Logs a pipeline run to the catalog."""
        run_data = {
            "timestamp": datetime.now().isoformat(),
            "dataset": dataset_name,
            "total_rows": total_rows,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "health_score": round((passed_checks / max(passed_checks + failed_checks, 1)) * 100, 2),
            "ai_analysis": ai_analysis_summary
        }
        
        with open(self.storage_path, 'r') as f:
            catalog = json.load(f)
            
        catalog.append(run_data)
        
        with open(self.storage_path, 'w') as f:
            json.dump(catalog, f, indent=4)
            
        logger.info(f"Logged run metadata for {dataset_name}. Health Score: {run_data['health_score']}%")

    def get_history(self) -> list:
        with open(self.storage_path, 'r') as f:
            return json.load(f)
