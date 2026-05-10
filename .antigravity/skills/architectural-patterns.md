# Skill: Data QA Architectural Patterns

## Overview
Designing a Data QA framework requires a different approach than traditional software QA. The focus is on data state, throughput, and stateful transformations.

## Core Patterns

### 1. The Data Test Pyramid
- **Unit Tests**: Test individual transformation functions (clean_phone_number).
- **Integration Tests**: Test Ingestion -> Transformation flow.
- **System/Contract Tests**: Test Source vs Target reconciliation.
- **End-to-End**: Test the final report/dashboard against the raw source.

### 2. Contract-First Testing
- Define a schema (Pydantic/JSON Schema) at the source.
- Validate every stage of the pipeline against this contract.
- Fail fast if the contract is violated.

### 3. Source-to-Target Reconciliation
- The "Gold Standard" of Data QA.
- Comparing aggregates (SUM, COUNT) and specific records between the source system and the warehouse.

### 4. Idempotent Data Setup
- Using Docker to spin up clean databases for every test run.
- Using `factory_boy` or similar for generating reproducible synthetic data.

### 5. Decoupled Validation Engine
- Separation of Concerns:
    - **Collector**: Gets data from Source/S3/SQL.
    - **Validator**: Runs the rules (regex, ranges, relationships).
    - **Notifier**: Sends results to Slack/Allure/Database.

## Strategic Thinking
- **False Positives**: Design for "Low Noise" alerts.
- **Sampling**: For massive datasets, implement statistical sampling strategies.
- **Performance**: Use vectorization (Pandas/Polars) for large-scale checks to avoid bottlenecking the pipeline.
