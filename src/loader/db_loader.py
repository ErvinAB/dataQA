import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from src.utils.logger import setup_logger

load_dotenv()
logger = setup_logger("db_loader")

class PostgresLoader:
    """Handles loading DataFrames into PostgreSQL."""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.name = os.getenv("DB_NAME", "data_reliability_db")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")
        
        self.connection_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        self.engine = create_engine(self.connection_string)

    def load_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'replace'):
        """
        Loads a pandas DataFrame into a PostgreSQL table.
        
        Args:
            df: The DataFrame to load.
            table_name: Name of the target table.
            if_exists: What to do if table exists ('fail', 'replace', 'append').
        """
        try:
            logger.info(f"Loading {len(df)} rows into table '{table_name}'")
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
            logger.info(f"Successfully loaded table '{table_name}'")
        except Exception as e:
            logger.error(f"Error loading table '{table_name}': {str(e)}")
            raise

    def execute_query(self, query: str):
        """Executes a raw SQL query and returns the result as a DataFrame."""
        try:
            return pd.read_sql(query, self.engine)
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
