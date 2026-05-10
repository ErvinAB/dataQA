import yaml
from typing import List
from src.validation.engine import DataQualityValidator, ValidationResult
from src.utils.logger import setup_logger

logger = setup_logger("yaml_parser")

class YamlContractRunner:
    """
    Reads a declarative YAML data contract and translates it into 
    method calls against the DataQualityValidator engine.
    """
    
    def __init__(self, contract_path: str = "data_contracts.yml"):
        self.contract_path = contract_path
        try:
            with open(self.contract_path, 'r') as file:
                self.config = yaml.safe_load(file)
            logger.info(f"Loaded YAML Data Contracts from {contract_path}")
        except Exception as e:
            logger.error(f"Failed to load YAML config: {e}")
            self.config = {}

    def run_contracts(self, dataset_name: str, validator: DataQualityValidator) -> List[ValidationResult]:
        """
        Executes all checks defined in the YAML file for a specific dataset.
        """
        results = []
        datasets = self.config.get("datasets", {})
        
        if dataset_name not in datasets:
            logger.warning(f"No contracts defined for dataset '{dataset_name}'.")
            return results

        checks = datasets[dataset_name].get("checks", [])
        logger.info(f"Executing {len(checks)} declarative YAML checks for '{dataset_name}'")

        for check in checks:
            check_type = check.get("type")
            
            if check_type == "not_null":
                res = validator.check_not_null(check.get("columns", []))
                results.append(res)
            elif check_type == "pattern":
                res = validator.check_pattern(check.get("column"), check.get("regex"))
                results.append(res)
            elif check_type == "range":
                res = validator.check_range(
                    check.get("column"), 
                    min_val=check.get("min_val"), 
                    max_val=check.get("max_val")
                )
                results.append(res)
            elif check_type == "unique":
                res = validator.check_unique(check.get("columns", []))
                results.append(res)
            else:
                logger.warning(f"Unsupported check type in YAML: {check_type}")
                
        return results
