# Skill: SQL Testing & Reconciliation

## Overview
SQL is the language of the warehouse. A Master-level QA engineer writes complex queries to validate multi-million row tables with precision and speed.

## Reconciliation Patterns
- **Full Outer Join Recon**: Compare source vs target by joining on unique keys and identifying mismatched columns.
- **Hash-Based Validation**: Calculating an MD5 hash of an entire row to quickly compare data between systems without individual column checks.
- **Aggregate Fingerprinting**: Comparing SUM, COUNT, MIN, MAX across various dimensions (e.g., by Date, by Region).

## Schema Validation
- **Information Schema**: Querying metadata tables to ensure columns, types, and constraints match the specification.
- **Nullability & Default Constraints**: Verifying that the DB enforces business rules at the schema level.

## Performance Tuning for Tests
- **CTEs (Common Table Expressions)**: For readable, multi-step validation logic.
- **Indexing for Tests**: Ensuring validation queries don't take hours by using appropriate indexes or sampling.
- **Window Functions**: Using `ROW_NUMBER()` or `LAG()` to detect duplicates or sequence gaps.

## SQL Tools
- **SQLAlchemy / SQLModel**: For type-safe SQL in Python.
- **SQLFluff**: For linting validation queries.

## Common Patterns

### Duplicate Detection
```sql
SELECT business_key, COUNT(*)
FROM table_name
GROUP BY business_key
HAVING COUNT(*) > 1;
```

### Null Detection
```sql
SELECT COUNT(*)
FROM table_name
WHERE required_column IS NULL;
```

### Row Count Reconciliation
```sql
SELECT COUNT(*) FROM source_table;
SELECT COUNT(*) FROM target_table;
```

### Aggregate Reconciliation
```sql
SELECT SUM(amount), COUNT(*)
FROM source_table;

SELECT SUM(amount), COUNT(*)
FROM target_table;
```

### Freshness Check
```sql
SELECT MAX(updated_at)
FROM table_name;
```
