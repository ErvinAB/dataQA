# Skill: Advanced Data Validation

## Overview
Validation in a Master-level framework moves beyond simple "null checks" into structural integrity and statistical consistency.

## Structural Validation (Pydantic)
- **Schema Enforcement**: Use Pydantic models to define the "perfect record".
- **Type Casting**: Automatic conversion of types with strict validation.
- **Custom Validators**: Complex cross-field logic (e.g., `end_date` must be after `start_date`).

## Content Validation
- **Regex & Patterns**: Email, Phone, SSN, specialized IDs.
- **Reference Integrity**: Ensuring Foreign Keys in the target exist in the source.
- **Business Rule Logic**: Custom Python functions for domain-specific rules.

## Statistical Validation
- **Z-Score Outliers**: Detecting values that deviate significantly from the mean.
- **Benford's Law**: Detecting fraudulent or unnatural numerical distributions.
- **Null-Rate Thresholds**: Failing if the null rate of a critical column exceeds 5%.

## Performance Optimization
- **Vectorized Checks**: Use Pandas/Numpy for performance.
- **Sampling Strategy**: For multi-million row datasets, use stratified sampling to maintain speed without losing coverage.
