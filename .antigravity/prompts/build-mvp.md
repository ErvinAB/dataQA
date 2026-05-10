# Prompt: Build MVP Repository

Build the first version of the Data Reliability Suite.

## Create this structure

```text
data-reliability-suite/
├── data/
│   ├── raw/
│   ├── transformed/
│   └── expected/
├── src/
│   ├── config/
│   ├── ingestion/
│   ├── transformation/
│   ├── loaders/
│   ├── validations/
│   ├── reporting/
│   └── utils/
├── tests/
│   ├── pipeline/
│   ├── database/
│   └── data_quality/
├── reports/
├── scripts/
├── .github/workflows/
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── README.md
└── .env.example
```

## MVP Behavior
1. Read raw CSV files from `data/raw`.
2. Transform the data into cleaned output.
3. Load transformed data into PostgreSQL.
4. Run pytest validations.
5. Generate readable test/report output.
6. Support GitHub Actions.

## Sample Domain
Use a simple but realistic online gaming/payment analytics domain:
- players
- transactions
- game_sessions

Avoid sensitive or real gambling data. Use fake sample data only.

## Validation Examples
- player_id must not be null
- transaction_id must be unique
- transaction amount must be greater than 0
- transaction currency must be valid
- game session duration must not be negative
- source and warehouse row counts must match
- latest transaction timestamp must not be stale
