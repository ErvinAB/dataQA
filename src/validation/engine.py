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
    failed_indices: Optional[List[int]] = None

class DataQualityValidator:
    """Core engine for running data quality checks."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.all_failed_indices = set()

    def _record_failures(self, indices):
        """Helper to track all failed rows across multiple checks."""
        self.all_failed_indices.update(indices)

    def check_not_null(self, columns: List[str]) -> ValidationResult:
        """Checks if specified columns have null values."""
        null_mask = self.df[columns].isnull().any(axis=1)
        failed_idx = self.df[null_mask].index.tolist()
        
        null_counts = self.df[columns].isnull().sum().to_dict()
        failed_cols = {col: count for col, count in null_counts.items() if count > 0}
        
        if not failed_idx:
            return ValidationResult(success=True, check_name="not_null", message="No null values found.")
        else:
            self._record_failures(failed_idx)
            return ValidationResult(
                success=False, 
                check_name="not_null", 
                message=f"Null values found in columns: {list(failed_cols.keys())}",
                details=failed_cols,
                failed_indices=failed_idx
            )

    def check_unique(self, columns: List[str]) -> ValidationResult:
        """Checks if specified columns have unique values."""
        dupes = {}
        failed_idx = []
        for col in columns:
            dupe_mask = self.df.duplicated(subset=[col], keep=False)
            if dupe_mask.any():
                failed_idx.extend(self.df[dupe_mask].index.tolist())
                dupes[col] = int(dupe_mask.sum())
        
        failed_idx = list(set(failed_idx)) # deduplicate
        
        if not failed_idx:
            return ValidationResult(success=True, check_name="unique", message="All values are unique.")
        else:
            self._record_failures(failed_idx)
            return ValidationResult(
                success=False, 
                check_name="unique", 
                message=f"Duplicates found in columns: {list(dupes.keys())}",
                details=dupes,
                failed_indices=failed_idx
            )

    def check_accepted_values(self, column: str, accepted_values: List[Any]) -> ValidationResult:
        """Checks if column contains only accepted values."""
        invalid_mask = ~self.df[column].isin(accepted_values)
        failed_idx = self.df[invalid_mask].index.tolist()
        invalid_values = self.df[invalid_mask][column].unique().tolist()
        
        if not failed_idx:
            return ValidationResult(success=True, check_name="accepted_values", message=f"All values in '{column}' are valid.")
        else:
            self._record_failures(failed_idx)
            return ValidationResult(
                success=False, 
                check_name="accepted_values", 
                message=f"Invalid values found in '{column}': {invalid_values}",
                details={"invalid_values": invalid_values},
                failed_indices=failed_idx
            )

    def check_range(self, column: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> ValidationResult:
        """Checks if numeric values are within a range."""
        invalid_mask = pd.Series(False, index=self.df.index)
        
        if min_val is not None:
            invalid_mask = invalid_mask | (self.df[column] < min_val)
        if max_val is not None:
            invalid_mask = invalid_mask | (self.df[column] > max_val)
            
        failed_idx = self.df[invalid_mask].index.tolist()

        if not failed_idx:
            return ValidationResult(success=True, check_name="range", message=f"Values in '{column}' are within range.")
        else:
            self._record_failures(failed_idx)
            return ValidationResult(
                success=False, 
                check_name="range", 
                message=f"Values in '{column}' are out of range.",
                details={"out_of_range_count": len(failed_idx)},
                failed_indices=failed_idx
            )

    def check_row_count(self, expected_count: int, tolerance: float = 0.0) -> ValidationResult:
        """Compares actual row count against expected count (Dataset-level check, no row indices)."""
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
        valid_rows = self.df[column].dropna().astype(str)
        matches = valid_rows.str.match(pattern)
        invalid_mask = ~matches
        
        # We need the original indices of the invalid rows
        failed_idx = valid_rows[invalid_mask].index.tolist()
        
        if not failed_idx:
            return ValidationResult(success=True, check_name="pattern", message=f"All values in '{column}' match pattern '{pattern}'.")
        else:
            self._record_failures(failed_idx)
            return ValidationResult(
                success=False,
                check_name="pattern",
                message=f"Found {len(failed_idx)} values in '{column}' that do not match pattern '{pattern}'.",
                details={"invalid_count": len(failed_idx)},
                failed_indices=failed_idx
            )

    def check_cross_field_logic(self, col1: str, col2: str, operator: str) -> ValidationResult:
        """Validates logical relationships between two columns."""
        if operator == '<':
            invalid_mask = ~(self.df[col1] < self.df[col2])
        elif operator == '>':
            invalid_mask = ~(self.df[col1] > self.df[col2])
        elif operator == '<=':
            invalid_mask = ~(self.df[col1] <= self.df[col2])
        elif operator == '>=':
            invalid_mask = ~(self.df[col1] >= self.df[col2])
        elif operator == '==':
            invalid_mask = ~(self.df[col1] == self.df[col2])
        else:
            raise ValueError(f"Unsupported operator: {operator}")

        # Only consider rows where both are non-null
        valid_pairs_mask = self.df[col1].notnull() & self.df[col2].notnull()
        final_invalid_mask = invalid_mask & valid_pairs_mask
        failed_idx = self.df[final_invalid_mask].index.tolist()

        if not failed_idx:
            return ValidationResult(success=True, check_name="cross_field", message=f"Cross-field check {col1} {operator} {col2} passed.")
        else:
            self._record_failures(failed_idx)
            return ValidationResult(
                success=False,
                check_name="cross_field",
                message=f"Cross-field check failed for {len(failed_idx)} rows: {col1} {operator} {col2}",
                details={"invalid_rows": len(failed_idx)},
                failed_indices=failed_idx
            )
            
    def split_clean_and_quarantine(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Splits the dataframe into clean records (passed all checks) and 
        quarantined records (failed at least one check).
        Returns: (clean_df, bad_df)
        """
        if not self.all_failed_indices:
            return self.df.copy(), pd.DataFrame(columns=self.df.columns)
            
        bad_df = self.df.loc[list(self.all_failed_indices)].copy()
        clean_df = self.df.drop(index=list(self.all_failed_indices)).copy()
        
        logger.info(f"DLQ Split: {len(clean_df)} clean rows, {len(bad_df)} quarantined rows.")
        return clean_df, bad_df



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
