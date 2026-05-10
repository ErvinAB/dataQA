import pandas as pd
from abc import ABC, abstractmethod
from src.utils.logger import setup_logger

logger = setup_logger("transformation_engine")

class BaseTransformer(ABC):
    """Abstract base class for all data transformations."""
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Executes the transformation pipeline."""
        logger.info(f"Starting transformation for {self.__class__.__name__}")
        df_transformed = df.copy()
        df_transformed = self._clean(df_transformed)
        df_transformed = self._normalize(df_transformed)
        logger.info(f"Finished transformation for {self.__class__.__name__}")
        return df_transformed

    @abstractmethod
    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

class PlayerTransformer(BaseTransformer):
    """Transforms player data."""
    
    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        # Fill missing email with a placeholder
        df['email'] = df['email'].fillna('unknown@example.com')
        # Fill missing country
        df['country'] = df['country'].fillna('Unknown')
        return df

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        # Convert joined_at to datetime, handle errors by coercing to NaT
        df['joined_at'] = pd.to_datetime(df['joined_at'], errors='coerce')
        # Ensure age is numeric
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        return df

class TransactionTransformer(BaseTransformer):
    """Transforms transaction data."""
    
    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        # Ensure player_id exists
        df = df.dropna(subset=['player_id'])
        return df

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
        return df

class SessionTransformer(BaseTransformer):
    """Transforms session data."""
    
    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        df['started_at'] = pd.to_datetime(df['started_at'], errors='coerce')
        df['duration_seconds'] = pd.to_numeric(df['duration_seconds'], errors='coerce').fillna(0)
        return df
