# Phase 1: MVP Build Plan

## Task 1 — Initialize Project
- Create repository structure
- Add requirements.txt
- Add pytest.ini
- Add .env.example
- Add basic README skeleton

## Task 2 — Add Sample Data
Create fake CSV files:
- players.csv
- transactions.csv
- game_sessions.csv

Include both valid and intentionally invalid rows for testing.

## Task 3 — Build Ingestion Layer
- Read CSV files using pandas
- Validate file existence
- Return DataFrames
- Add logging

## Task 4 — Build Transformation Layer
- Clean raw data
- Normalize fields
- Convert timestamps
- Prepare warehouse-ready DataFrames

## Task 5 — Build PostgreSQL Loader
- Connect using SQLAlchemy
- Create tables if needed
- Load transformed data
- Support local Docker PostgreSQL

## Task 6 — Build Validation Engine
Implement reusable checks:
- not_null
- unique
- accepted_values
- greater_than
- row_count_match
- aggregate_match
- freshness
- schema_columns_match

## Task 7 — Add Pytest Tests
Create tests for:
- schema validation
- completeness
- duplicates
- business rules
- source-to-target reconciliation
- freshness

## Task 8 — Add Docker Compose
Add PostgreSQL service.

## Task 9 — Add GitHub Actions
Run tests on pull request and push.

## Task 10 — Final README
Make the README portfolio-ready.
