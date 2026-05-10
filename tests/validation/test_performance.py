import pytest
import pandas as pd
import numpy as np
import time
from src.validation.engine import DataQualityValidator

def test_performance_100k_rows():
    """
    Non-Functional Performance Test:
    Ensures that the validation engine can process 100,000 rows
    for standard rules (null checks, range checks, pattern checks)
    within an acceptable SLA (e.g., under 1.5 seconds).
    """
    # 1. Generate 100k rows of dummy data
    num_rows = 100_000
    df = pd.DataFrame({
        'player_id': np.arange(num_rows),
        'username': [f"user_{i}" for i in range(num_rows)],
        'email': [f"user_{i}@example.com" for i in range(num_rows)],
        'age': np.random.randint(18, 65, size=num_rows),
        'country': np.random.choice(['US', 'UK', 'CA', 'DE', 'FR'], size=num_rows)
    })
    
    validator = DataQualityValidator(df)
    
    # 2. Time the validation suite
    start_time = time.time()
    
    res_null = validator.check_not_null(['player_id', 'username', 'email'])
    res_range = validator.check_range('age', min_val=0, max_val=100)
    res_pattern = validator.check_pattern('email', r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # 3. Assertions
    assert res_null.success is True
    assert res_range.success is True
    assert res_pattern.success is True
    
    # SLA: Must process 100k rows in under 1.5 seconds
    # (Usually Pandas vectorized operations on 100k rows take < 0.2 seconds)
    print(f"\nPerformance Test: 100k rows validated in {execution_time:.4f} seconds.")
    assert execution_time < 1.5, f"Performance SLA violated. Took {execution_time} seconds."
