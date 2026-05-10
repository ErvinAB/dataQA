# Skill: Data Observability & Monitoring

## Overview
Data Observability goes beyond unit testing. It is the ability to understand the health of the data across the entire lifecycle through metadata, logs, and metrics.

## Key Pillars

### 1. Freshness (SLA/SLO)
- Monitoring the time since the last data update.
- Setting alerts for "Stale Data" based on business requirements.

### 2. Distribution (Volume & Schema)
- **Volume**: Detecting unexpected drops or spikes in row counts.
- **Schema Evolution**: Tracking breaking changes in data structure (new columns, changed types).

### 3. Lineage
- Understanding the "Source to Target" flow.
- Validating that transformations don't break downstream dependencies.

### 4. Anomaly Detection
- Using statistical methods (Z-score, Moving Averages) to find outliers in data distributions.
- AI-assisted anomaly detection for complex patterns.

## Implementation Patterns
- **Metadata Logging**: Storing every validation run in a metadata table (PostgreSQL).
- **Dashboards**: Visualizing data health trends (Grafana/Streamlit).
- **Circuit Breakers**: Stopping a pipeline if critical data quality checks fail.

## Tools of the Trade
- **Great Expectations**: For declarative data contracts.
- **dbt-tests**: For integrated transformation testing.
- **Monte Carlo / Bigeye**: (Conceptual) Enterprise-grade observability patterns.
