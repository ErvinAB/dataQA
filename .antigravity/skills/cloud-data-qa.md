# Cloud Data QA Strategy

Testing modern cloud data architectures (AWS, GCP, Azure) requires specific domain knowledge.

## 1. Data Lakes (e.g., AWS S3)
Data Lakes store raw, unstructured, or semi-structured data.
- **File Format Testing:** Validate that files land in the correct format (e.g., Parquet instead of CSV for performance).
- **Partitioning Strategy:** Check if data is correctly partitioned in the bucket (e.g., `s3://bucket/year=2024/month=05/`).
- **Access Control (IAM):** Ensure that only authorized roles can read/write to specific buckets.

## 2. Cloud Data Warehouses (e.g., Snowflake, Redshift, BigQuery)
- **Cost Testing:** Poorly optimized queries in BigQuery/Snowflake cost money. QA should include query cost/efficiency checks.
- **Zero-Copy Cloning:** Use Snowflake's cloning features to create exact replicas of production data instantly for UAT or integration testing without duplicating storage costs.

## 3. Cloud Orchestration (e.g., MWAA / Airflow)
- Test DAGs (Directed Acyclic Graphs) locally using Docker before deploying to the cloud.
- Ensure proper dependency management and alert routing (e.g., routing failures to an SNS topic -> PagerDuty).
