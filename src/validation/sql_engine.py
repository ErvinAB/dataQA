import pandas as pd
from src.loader.db_loader import PostgresLoader
from src.utils.logger import setup_logger

logger = setup_logger("sql_engine")

class WarehouseValidator:
    """
    Executes complex data integrity validations directly inside the Data Warehouse.
    Proves SQL proficiency and understanding of post-load ELT checks.
    """
    
    def __init__(self, loader: PostgresLoader):
        self.loader = loader

    def check_referential_integrity(self, child_table: str, child_fk: str, parent_table: str, parent_pk: str) -> bool:
        """
        Validates that all foreign keys in the child table exist in the parent table.
        Example: Find orphaned transactions where player_id doesn't exist in players.
        """
        logger.info(f"Running SQL Integrity Check: {child_table}.{child_fk} -> {parent_table}.{parent_pk}")
        
        query = f"""
            SELECT COUNT(1) as orphaned_count
            FROM {child_table} c
            LEFT JOIN {parent_table} p ON c.{child_fk} = p.{parent_pk}
            WHERE p.{parent_pk} IS NULL
        """
        
        try:
            df = self.loader.execute_query(query)
            orphans = int(df.iloc[0]['orphaned_count'])
            
            if orphans == 0:
                logger.info("✅ Referential integrity intact. No orphaned records found.")
                return True
            else:
                logger.error(f"❌ Referential integrity failure! Found {orphans} orphaned records in {child_table}.")
                return False
        except Exception as e:
            logger.error(f"SQL Validation Failed: {str(e)}")
            return False

    def check_business_logic(self, query: str, expected_count: int = 0) -> bool:
        """
        Runs a custom SQL query representing a business rule violation.
        By default, expects 0 rows returned (meaning no violations).
        """
        logger.info(f"Running Custom SQL Business Logic Check...")
        try:
            df = self.loader.execute_query(query)
            violation_count = len(df)
            
            if violation_count == expected_count:
                logger.info(f"✅ Business logic check passed.")
                return True
            else:
                logger.error(f"❌ Business logic check failed! Found {violation_count} violations (Expected: {expected_count}).")
                return False
        except Exception as e:
            logger.error(f"SQL Validation Failed: {str(e)}")
            return False
