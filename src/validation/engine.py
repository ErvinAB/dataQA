import pandas as pd
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ValidationError, Field, field_validator
from datetime import datetime
import re
from src.utils.logger import setup_logger

logger = setup_logger("validation_engine")

class ValidationResult(BaseModel):
    """Container for validation results."""
    success: bool
    check_name: str
    message: str
    details: Optional[Dict[str, Any]] = None

class DataQualityValidator:
    """Core engine for running data quality checks."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def check_not_null(self, columns: List[str]) -> ValidationResult:
        """Checks if specified columns have null values."""
        null_counts = self.df[columns].isnull().sum().to_dict()
        failed_cols = {col: count for col, count in null_counts.items() if count > 0}
        
        if not failed_cols:
            return ValidationResult(success=True, check_name="not_null", message="No null values found.")
        else:
            return ValidationResult(
                success=False, 
                check_name="not_null", 
                message=f"Null values found in columns: {list(failed_cols.keys())}",
                details=failed_cols
            )

    def check_unique(self, columns: List[str]) -> ValidationResult:
        """Checks if specified columns have unique values."""
        dupes = {}
        for col in columns:
            dupe_count = self.df[col].duplicated().sum()
            if dupe_count > 0:
                dupes[col] = int(dupe_count)
        
        if not dupes:
            return ValidationResult(success=True, check_name="unique", message="All values are unique.")
        else:
            return ValidationResult(
                success=False, 
                check_name="unique", 
                message=f"Duplicates found in columns: {list(dupes.keys())}",
                details=dupes
            )

    def check_accepted_values(self, column: str, accepted_values: List[Any]) -> ValidationResult:
        """Checks if column contains only accepted values."""
        invalid_values = self.df[~self.df[column].isin(accepted_values)][column].unique().tolist()
        
        if not invalid_values:
            return ValidationResult(success=True, check_name="accepted_values", message=f"All values in '{column}' are valid.")
        else:
            return ValidationResult(
                success=False, 
                check_name="accepted_values", 
                message=f"Invalid values found in '{column}': {invalid_values}",
                details={"invalid_values": invalid_values}
            )

    def check_range(self, column: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> ValidationResult:
        """Checks if numeric values are within a range."""
        if min_val is not None and max_val is not None:
            invalid_df = self.df[(self.df[column] < min_val) | (self.df[column] > max_val)]
        elif min_val is not None:
            invalid_df = self.df[self.df[column] < min_val]
        elif max_val is not None:
            invalid_df = self.df[self.df[column] > max_val]
        else:
            return ValidationResult(success=True, check_name="range", message="No range specified.")

        if invalid_df.empty:
            return ValidationResult(success=True, check_name="range", message=f"Values in '{column}' are within range.")
        else:
            return ValidationResult(
                success=False, 
                check_name="range", 
                message=f"Values in '{column}' are out of range.",
                details={"out_of_range_count": len(invalid_df)}
            )

    def check_row_count(self, expected_count: int, tolerance: float = 0.0) -> ValidationResult:
        """Compares actual row count against expected count."""
        actual_count = len(self.df)
        diff = abs(actual_count - expected_count)
        allowed_diff = expected_count * tolerance
        
        if diff <= allowed_diff:
            return ValidationResult(success=True, check_name="row_count", message=f"Row count {actual_count} matches expected {expected_count}.")
        else:
            return ValidationResult(
                success=False, 
                check_name="row_count", 
                message=f"Row count {actual_count} does not match expected {expected_count} (diff: {diff}).",
                details={"actual": actual_count, "expected": expected_count, "diff": diff}
            )

    def check_pattern(self, column: str, pattern: str) -> ValidationResult:
        """Checks if string values in a column match a specific regex pattern."""
        # Dropna so we only test valid strings, null checks are handled elsewhere
        valid_rows = self.df[column].dropna().astype(str)
        matches = valid_rows.str.match(pattern)
        invalid_count = (~matches).sum()
        
        if invalid_count == 0:
            return ValidationResult(success=True, check_name="pattern", message=f"All values in '{column}' match pattern '{pattern}'.")
        else:
            return ValidationResult(
                success=False,
                check_name="pattern",
                message=f"Found {invalid_count} values in '{column}' that do not match pattern '{pattern}'.",
                details={"invalid_count": int(invalid_count)}
            )

    def check_cross_field_logic(self, col1: str, col2: str, operator: str) -> ValidationResult:
        """
        Validates logical relationships between two columns (e.g., 'start_date' < 'end_date').
        Supported operators: '<', '>', '<=', '>=', '=='
        """
        if operator == '<':
            invalid = self.df[~(self.df[col1] < self.df[col2])]
        elif operator == '>':
            invalid = self.df[~(self.df[col1] > self.df[col2])]
        elif operator == '<=':
            invalid = self.df[~(self.df[col1] <= self.df[col2])]
        elif operator == '>=':
            invalid = self.df[~(self.df[col1] >= self.df[col2])]
        elif operator == '==':
            invalid = self.df[~(self.df[col1] == self.df[col2])]
        else:
            raise ValueError(f"Unsupported operator: {operator}")

        # Filter out rows where either column is null, since we only want to test existing pairs
        invalid = invalid.dropna(subset=[col1, col2])

        if invalid.empty:
            return ValidationResult(success=True, check_name="cross_field", message=f"Cross-field check {col1} {operator} {col2} passed.")
        else:
            return ValidationResult(
                success=False,
                check_name="cross_field",
                message=f"Cross-field check failed for {len(invalid)} rows: {col1} {operator} {col2}",
                details={"invalid_rows": len(invalid)}
            )


class PlayerRecord(BaseModel):
    """Pydantic model for advanced structural validation of a player."""
    player_id: int
    username: str
    email: str = Field(pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    joined_at: datetime
    country: str
    age: int = Field(ge=0, le=120)

    @field_validator('username')
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Username cannot be empty')
        return v
