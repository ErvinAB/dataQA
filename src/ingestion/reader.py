import pandas as pd
import os
from src.utils.logger import setup_logger

logger = setup_logger("ingestion_reader")

class DataReader:
    """Handles reading raw data from various sources (Local and Cloud)."""
    
    @staticmethod
    def read_csv(file_path: str) -> pd.DataFrame:
        """
        Reads a CSV file into a pandas DataFrame.
        Supports local paths and simulated 's3://' Cloud Data Lake paths.
        
        Args:
            file_path: Path to the CSV file (e.g., 'data/raw/players.csv' or 's3://dataQA-lake/raw/players.csv').
            
        Returns:
            pd.DataFrame: The loaded data.
        """
        is_s3 = file_path.startswith("s3://")
        
        if is_s3:
            logger.info(f"☁️ Cloud Ingestion: Simulating connection to AWS S3 bucket for {file_path}")
            # Mock S3 by stripping the bucket info and mapping to local 'data/' directory
            local_path = file_path.replace("s3://dataQA-lake/", "data/")
            logger.info(f"☁️ Cloud Ingestion: Downloading object to temporary memory (mocked via {local_path})")
        else:
            local_path = file_path

        if not os.path.exists(local_path):
            logger.error(f"File not found: {local_path}")
            raise FileNotFoundError(f"Data file not found at: {local_path}")
        
        try:
            logger.info(f"Reading CSV data...")
            df = pd.read_csv(local_path)
            logger.info(f"Successfully loaded {len(df)} rows.")
            return df
        except Exception as e:
            logger.error(f"Error reading CSV {local_path}: {str(e)}")
            raise
