# Skill: Enterprise Pytest Framework

## Overview
Pytest is our engine. For a Master-level suite, we leverage advanced fixtures, parameterization, and custom plugins to create a flexible testing surface.

## Advanced Fixtures
- **Scope Management**: Use `session` scope for DB connections and `function` scope for test data.
- **Yield Fixtures**: Ensure clean teardown (e.g., dropping temp tables after a test).
- **Mocking**: Using `unittest.mock` or `pytest-mock` to isolate external dependencies (S3, APIs).

## Parameterization
- **Data-Driven Testing**: Use `@pytest.mark.parametrize` to run the same validation against multiple tables or datasets.
- **Dynamic IDs**: Custom IDs for parameterized tests to make reports readable.

## Custom Markers
- **Categorization**: Use `@pytest.mark.smoke`, `@pytest.mark.regression`, `@pytest.mark.slow` to selectively run tests.
- **Dependency Markers**: Prevent downstream tests from running if a setup test fails.

## Plugins & Reporting
- **pytest-xdist**: For parallel execution of independent data checks.
- **pytest-html / Allure**: For professional, stakeholder-ready quality reports.
- **pytest-cov**: Ensuring our validation logic itself is well-tested.

## Test Naming Style
Good:
- test_orders_have_no_duplicate_order_ids
- test_customer_email_is_required
- test_source_and_warehouse_order_counts_match
- test_latest_transaction_data_is_fresh

Bad:
- test_1
- test_data
- test_check
