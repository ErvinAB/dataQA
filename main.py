import os
import pandas as pd
from dotenv import load_dotenv
from src.ingestion.reader import DataReader
from src.transformation.transformer import PlayerTransformer, TransactionTransformer, SessionTransformer
from src.loader.db_loader import PostgresLoader
from src.validation.engine import DataQualityValidator
from src.ai_agents.summarizer import AIFailureSummarizer
from src.ai_agents.drift_detector import DataDriftDetector
from src.observability.anomaly_engine import AnomalyEngine
from src.observability.metadata_catalog import MetadataCatalog
from src.utils.logger import setup_logger

load_dotenv()
logger = setup_logger("main_pipeline")

def run_pipeline():
    logger.info("Starting Data Reliability Suite (Master-Level Pipeline)...")
    
    # 1. Ingestion
    reader = DataReader()
    df_players_raw = reader.read_csv("data/raw/players.csv")
    df_transactions_raw = reader.read_csv("data/raw/transactions.csv")
    df_sessions_raw = reader.read_csv("data/raw/game_sessions.csv")
    
    # 2. Observability: Volume Anomaly Detection
    logger.info("Running Volume Anomaly Detection...")
    anomaly_engine = AnomalyEngine()
    # Simulating historical data
    hist_counts = [10, 11, 10, 12, 10, 11, 10]
    anomaly_res = anomaly_engine.detect_volume_anomaly(len(df_players_raw), hist_counts)
    
    # 3. Validation (Pre-transformation)
    logger.info("Running Data Quality Validations...")
    v_players = DataQualityValidator(df_players_raw)
    
    # Collect validation results
    validation_results = []
    res_null = v_players.check_not_null(['player_id', 'username'])
    validation_results.append(res_null)
    
    res_pattern = v_players.check_pattern('email', r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    validation_results.append(res_pattern)
    
    # 4. AI Agents: Failure Summarization
    failed_checks = [res.model_dump() for res in validation_results if not res.success]
    passed_checks_count = len(validation_results) - len(failed_checks)
    
    summarizer = AIFailureSummarizer()
    ai_report = summarizer.generate_root_cause_analysis(failed_checks)
    
    print("\n" + "="*50)
    print(ai_report)
    print("="*50 + "\n")
    
    # 5. AI Agents: Data Drift Detection
    # Simulating reference data (e.g., from yesterday)
    df_players_ref = df_players_raw.copy()
    # Artificially shift age to simulate drift for the example
    df_players_raw['age'] = pd.to_numeric(df_players_raw['age'], errors='coerce')
    df_players_ref['age'] = pd.to_numeric(df_players_ref['age'], errors='coerce') + 15 
    
    drift_detector = DataDriftDetector()
    drift_res = drift_detector.detect_drift(df_players_ref, df_players_raw, ["age"])

    # 6. Observability: Metadata Logging
    catalog = MetadataCatalog()
    catalog.log_run(
        dataset_name="players_pipeline",
        total_rows=len(df_players_raw),
        failed_checks=len(failed_checks),
        passed_checks=passed_checks_count,
        ai_analysis_summary="Drift Detected" if drift_res["drift_detected"] else "Clean Run"
    )
    
    # 7. Transformation
    logger.info("Running transformations...")
    p_transformer = PlayerTransformer()
    df_players_clean = p_transformer.transform(df_players_raw)
    
    t_transformer = TransactionTransformer()
    df_transactions_clean = t_transformer.transform(df_transactions_raw)
    
    s_transformer = SessionTransformer()
    df_sessions_clean = s_transformer.transform(df_sessions_raw)
    
    # 8. Loader
    try:
        loader = PostgresLoader()
        loader.load_dataframe(df_players_clean, "players")
        loader.load_dataframe(df_transactions_clean, "transactions")
        loader.load_dataframe(df_sessions_clean, "game_sessions")
    except Exception as e:
        logger.warning(f"Skipping DB load: {str(e)}. (Ensure Docker Postgres is running)")

    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()

