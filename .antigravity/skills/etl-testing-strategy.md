# ETL Testing Strategy

As an expert Data QA / DRE, testing ETL (Extract, Transform, Load) pipelines requires a shift from traditional software testing to data-centric testing.

## 1. Functional Testing
Validates the business logic and data transformations.
- **Source-to-Target Mapping:** Does data in the source correctly map to the target schema?
- **Transformation Logic:** Do custom calculations (e.g., currency conversion, age calculation) work exactly as per business requirements?
- **Data Completeness:** Did all expected records make it from Source to Target?
- **Data Integrity:** Are foreign keys respected? Are there orphans?

## 2. Non-Functional Testing
Validates the system's behavior under various conditions.
- **Performance/Scalability:** Can the validation and transformation engine process 10 million rows within the required SLA? (Use Pytest with `time` or `pytest-benchmark`).
- **Resilience/Recovery:** If the pipeline fails midway, can it restart without duplicating data (idempotency)?
- **Data Security:** Is PII (Personally Identifiable Information) correctly masked or hashed during the extraction phase?

## 3. User Acceptance Testing (UAT) for Data
Partnering with Business Analysts and downstream consumers (e.g., BI teams, Data Scientists).
- Ensure the final Data Mart or Reporting Layer meets the business requirements.
- Use tools like Tableau, PowerBI, or Metabase to visualize the test data and confirm dashboards render correctly.
