import pytest
import pandas as pd
from src.transformation.transformer import PlayerTransformer, TransactionTransformer

def test_player_transformer_cleaning():
    raw_data = {
        'player_id': [1, 2],
        'username': ['user1', 'user2'],
        'email': [None, 'test@test.com'],
        'joined_at': ['2023-01-01', '2023-01-02'],
        'country': [None, 'USA'],
        'age': [25, 30]
    }
    df = pd.DataFrame(raw_data)
    transformer = PlayerTransformer()
    
    transformed_df = transformer.transform(df)
    
    assert transformed_df.iloc[0]['email'] == 'unknown@example.com'
    assert transformed_df.iloc[0]['country'] == 'Unknown'
    assert isinstance(transformed_df.iloc[0]['joined_at'], pd.Timestamp)

def test_transaction_transformer_orphans():
    raw_data = {
        'transaction_id': ['T1', 'T2'],
        'player_id': [1, None],
        'amount': [10.0, 20.0],
        'currency': ['USD', 'USD'],
        'created_at': ['2023-01-01', '2023-01-02']
    }
    df = pd.DataFrame(raw_data)
    transformer = TransactionTransformer()
    
    transformed_df = transformer.transform(df)
    
    # Should drop the row with null player_id
    assert len(transformed_df) == 1
    assert transformed_df.iloc[0]['transaction_id'] == 'T1'
