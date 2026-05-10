import json
import os
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger("data_lineage")

class LineageTracker:
    """
    Tracks the flow of data through the ETL pipeline, mimicking tools like OpenLineage.
    """
    def __init__(self, output_file: str = "data/metadata/lineage.json"):
        self.output_file = output_file
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.nodes = []
        self.edges = []
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    def add_node(self, node_id: str, type: str, description: str):
        self.nodes.append({
            "id": node_id,
            "type": type,
            "description": description
        })
        
    def add_edge(self, source_id: str, target_id: str, action: str, row_count: int = None):
        self.edges.append({
            "source": source_id,
            "target": target_id,
            "action": action,
            "row_count": row_count
        })

    def save_lineage(self):
        lineage_data = {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "nodes": self.nodes,
            "edges": self.edges
        }
        
        try:
            with open(self.output_file, 'w') as f:
                json.dump(lineage_data, f, indent=4)
            logger.info(f"Data Lineage map saved to {self.output_file}")
        except Exception as e:
            logger.error(f"Failed to save data lineage: {e}")
