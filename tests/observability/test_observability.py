import pytest
import os
import json
from src.observability.anomaly_engine import AnomalyEngine
from src.observability.metadata_catalog import MetadataCatalog

def test_anomaly_engine_no_anomaly():
    engine = AnomalyEngine(z_threshold=3.0)
    res = engine.detect_volume_anomaly(102, [100, 102, 98, 101, 99])
    assert res["is_anomaly"] is False

def test_anomaly_engine_with_anomaly():
    engine = AnomalyEngine(z_threshold=3.0)
    res = engine.detect_volume_anomaly(500, [100, 102, 98, 101, 99])
    assert res["is_anomaly"] is True

def test_anomaly_engine_insufficient_history():
    engine = AnomalyEngine()
    res = engine.detect_volume_anomaly(100, [100])
    assert res["is_anomaly"] is False
    assert "reason" in res

def test_metadata_catalog(tmp_path):
    catalog_path = tmp_path / "metadata.json"
    catalog = MetadataCatalog(storage_path=str(catalog_path))
    
    catalog.log_run("players", 100, failed_checks=2, passed_checks=8, ai_analysis_summary="Mock analysis")
    
    history = catalog.get_history()
    assert len(history) == 1
    assert history[0]["dataset"] == "players"
    assert history[0]["health_score"] == 80.0
