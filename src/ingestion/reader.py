import pandas as pd
import os
from src.utils.logger import setup_logger

logger = setup_logger("ingestion_reader")

class DataReader:
    """Handles reading raw data from various sources."""
    
    @staticmethod
    def read_csv(file_path: str) -> pd.DataFrame:
        """
        Reads a CSV file into a pandas DataFrame.
        
        Args:
            file_path: Absolute or relative path to the CSV file.
            
        Returns:
            pd.DataFrame: The loaded data.
            
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"CSV file not found at: {file_path}")
        
        try:
            logger.info(f"Reading CSV from {file_path}")
            df = pd.read_csv(file_path)
            logger.info(f"Successfully loaded {len(df)} rows from {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error reading CSV {file_path}: {str(e)}")
            raise
