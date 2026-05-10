import pytest
import pandas as pd
from src.validation.engine import DataQualityValidator

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'id': [1, 2, 3, 3],
        'val': [10, 20, 30, None],
        'cat': ['A', 'B', 'A', 'C']
    })

def test_check_not_null(sample_df):
    validator = DataQualityValidator(sample_df)
    result = validator.check_not_null(['id'])
    assert result.success is True
    
    result_fail = validator.check_not_null(['val'])
    assert result_fail.success is False
    assert result_fail.details['val'] == 1

def test_check_unique(sample_df):
    validator = DataQualityValidator(sample_df)
    result = validator.check_unique(['id'])
    assert result.success is False
    assert result.details['id'] == 2

def test_check_accepted_values(sample_df):
    validator = DataQualityValidator(sample_df)
    result = validator.check_accepted_values('cat', ['A', 'B'])
    assert result.success is False
    assert 'C' in result.details['invalid_values']

def test_check_range(sample_df):
    validator = DataQualityValidator(sample_df)
    result = validator.check_range('val', min_val=0, max_val=25)
    assert result.success is False
    assert result.details['out_of_range_count'] == 1 # value 30

def test_check_pattern():
    df = pd.DataFrame({'email': ['test@test.com', 'invalid-email', 'ok@ok.org']})
    validator = DataQualityValidator(df)
    result = validator.check_pattern('email', r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    assert result.success is False
    assert result.details['invalid_count'] == 1

def test_check_cross_field_logic():
    df = pd.DataFrame({
        'start': [1, 2, 5],
        'end': [2, 3, 4]
    })
    validator = DataQualityValidator(df)
    result = validator.check_cross_field_logic('start', 'end', '<')
    assert result.success is False
    assert result.details['invalid_rows'] == 1 # row 3 where start=5, end=4
