import os
import time
import pandas as pd
from dotenv import load_dotenv
from prometheus_client import start_http_server, Counter, Gauge
from src.ingestion.reader import DataReader
from src.transformation.transformer import PlayerTransformer, TransactionTransformer, SessionTransformer
from src.loader.db_loader import PostgresLoader
from src.validation.engine import DataQualityValidator
from src.validation.sql_engine import WarehouseValidator
from src.validation.yaml_parser import YamlContractRunner
from src.ai_agents.summarizer import AIFailureSummarizer
from src.observability.metadata_catalog import MetadataCatalog
from src.utils.logger import setup_logger
from src.observability.lineage import LineageTracker

load_dotenv()
logger = setup_logger("main_pipeline")

# --- Prometheus Metrics Definition ---
PIPELINE_RUNS = Counter('dataqa_pipeline_runs_total', 'Total number of pipeline executions')
ROWS_PROCESSED = Counter('dataqa_rows_processed_total', 'Total rows processed by the pipeline')
HEALTH_SCORE = Gauge('dataqa_health_score', 'Data quality health score percentage')
DRIFT_DETECTED = Gauge('dataqa_drift_detected', '1 if drift detected, 0 otherwise')

def run_pipeline():
    PIPELINE_RUNS.inc()
    logger.info("Starting Data Reliability Suite (Master-Level Pipeline)...")
    
    # 0. Initialize Lineage Tracker
    lineage = LineageTracker()
    lineage.add_node("s3_raw_players", "source", "S3 Bucket: s3://dataQA-lake/raw/players.csv")
    
    # 1. Ingestion (Simulating S3)
    reader = DataReader()
    df_players_raw = reader.read_csv("s3://dataQA-lake/raw/players.csv")
    df_transactions_raw = reader.read_csv("s3://dataQA-lake/raw/transactions.csv")
    df_sessions_raw = reader.read_csv("s3://dataQA-lake/raw/game_sessions.csv")
    
    total_rows = len(df_players_raw) + len(df_transactions_raw) + len(df_sessions_raw)
    ROWS_PROCESSED.inc(total_rows)
    
    lineage.add_node("validation_engine", "process", "DataQualityValidator Engine")
    lineage.add_edge("s3_raw_players", "validation_engine", "read", len(df_players_raw))
    
    # 2. Observability: Volume Anomaly Detection
    logger.info("Running Volume Anomaly Detection...")
    anomaly_engine = AnomalyEngine()
    hist_counts = [10, 11, 10, 12, 10, 11, 10]
    anomaly_res = anomaly_engine.detect_volume_anomaly(len(df_players_raw), hist_counts)
    
    # 3. Validation
    logger.info("Running Data Quality Validations via YAML Contracts...")
    v_players = DataQualityValidator(df_players_raw)
    yaml_runner = YamlContractRunner()
    
    validation_results = yaml_runner.run_contracts("players", v_players)
    
    # DLQ / Quarantine Split
    df_players_clean, df_players_quarantine = v_players.split_clean_and_quarantine()
    
    lineage.add_node("clean_data", "dataset", "Clean validated memory dataframe")
    lineage.add_edge("validation_engine", "clean_data", "pass", len(df_players_clean))
    
    if not df_players_quarantine.empty:
        quarantine_path = "data/quarantine/players_quarantine.csv"
        df_players_quarantine.to_csv(quarantine_path, index=False)
        logger.warning(f"🚨 DLQ Alert: {len(df_players_quarantine)} rows quarantined to {quarantine_path}")
        lineage.add_node("quarantine_csv", "sink", "Dead Letter Queue CSV")
        lineage.add_edge("validation_engine", "quarantine_csv", "quarantine", len(df_players_quarantine))
    
    # 4. AI Agents: Failure Summarization
    failed_checks = [res.model_dump() for res in validation_results if not res.success]
    passed_checks_count = len(validation_results) - len(failed_checks)
    
    summarizer = AIFailureSummarizer()
    ai_report = summarizer.generate_root_cause_analysis(failed_checks)
    print("\n" + "="*50 + "\n" + ai_report + "\n" + "="*50 + "\n")
    
    # 5. AI Agents: Data Drift Detection (Only on clean data)
    df_players_ref = df_players_clean.copy()
    df_players_clean['age'] = pd.to_numeric(df_players_clean['age'], errors='coerce')
    df_players_ref['age'] = pd.to_numeric(df_players_ref['age'], errors='coerce') + 15 
    
    drift_detector = DataDriftDetector(enforce_failure=True)
    try:
        drift_res = drift_detector.detect_drift(df_players_ref, df_players_clean, ["age"])
        drift_detected = drift_res["drift_detected"]
    except Exception as e:
        logger.error(f"Pipeline Halted due to AI Quality Check: {e}")
        DRIFT_DETECTED.set(1)
        lineage.save_lineage()
        raise e
        
    DRIFT_DETECTED.set(1 if drift_detected else 0)

    # 6. Observability: Metadata Logging
    catalog = MetadataCatalog()
    catalog.log_run(
        dataset_name="players_pipeline",
        total_rows=len(df_players_raw),
        failed_checks=len(failed_checks),
        passed_checks=passed_checks_count,
        ai_analysis_summary="Drift Detected" if drift_res["drift_detected"] else "Clean Run"
    )
    
    # Update Health Score Metric
    health = (passed_checks_count / max(passed_checks_count + len(failed_checks), 1)) * 100
    HEALTH_SCORE.set(health)
    
    # 7. Transformation
    logger.info("Running transformations...")
    df_players_transformed = PlayerTransformer().transform(df_players_clean)
    df_transactions_clean = TransactionTransformer().transform(df_transactions_raw)
    df_sessions_clean = SessionTransformer().transform(df_sessions_raw)
    
    lineage.add_node("transformation_engine", "process", "Business Logic Transformation")
    lineage.add_edge("clean_data", "transformation_engine", "transform", len(df_players_transformed))
    
    # 8. Load & Warehouse Validation
    try:
        loader = PostgresLoader()
        loader.load_dataframe(df_players_transformed, "players")
        loader.load_dataframe(df_transactions_clean, "transactions")
        loader.load_dataframe(df_sessions_clean, "game_sessions")
        
        lineage.add_node("postgres_warehouse", "sink", "PostgreSQL players table")
        lineage.add_edge("transformation_engine", "postgres_warehouse", "load", len(df_players_transformed))
        
        # Post-Load SQL Validation
        logger.info("Running Post-Load Warehouse Validations...")
        sql_validator = WarehouseValidator(loader)
        sql_validator.check_referential_integrity(
            child_table="transactions", 
            child_fk="player_id", 
            parent_table="players", 
            parent_pk="player_id"
        )
    except Exception as e:
        logger.warning(f"Skipping DB load and SQL validation: {str(e)}. (Ensure Docker Postgres is running)")

    # Save the lineage map
    lineage.save_lineage()
    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    # Start Prometheus Metrics Server on port 8000
    logger.info("Starting Prometheus Metrics Server on port 8000...")
    start_http_server(8000)
    
    # Run pipeline once
    run_pipeline()
    
    # Keep main thread alive to allow metrics scraping for 30 seconds
    logger.info("Pipeline finished. Keeping metrics server alive for 30 seconds for scraping...")
    time.sleep(30)


