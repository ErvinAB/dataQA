import pytest
import os
import pandas as pd
from src.ingestion.reader import DataReader

def test_read_csv_success(tmp_path):
    # Setup
    d = tmp_path / "subdir"
    d.mkdir()
    p = d / "test.csv"
    p.write_text("id,name\n1,alice\n2,bob")
    
    # Execute
    df = DataReader.read_csv(str(p))
    
    # Assert
    assert len(df) == 2
    assert list(df.columns) == ["id", "name"]
    assert df.iloc[0]["name"] == "alice"

def test_read_csv_not_found():
    with pytest.raises(FileNotFoundError):
        DataReader.read_csv("non_existent_file.csv")

@pytest.mark.ingestion
def test_read_sample_players():
    # This test reads from the actual data/raw folder
    path = "data/raw/players.csv"
    if os.path.exists(path):
        df = DataReader.read_csv(path)
        assert not df.empty
        assert "player_id" in df.columns
    else:
        pytest.skip("Sample data not found")
