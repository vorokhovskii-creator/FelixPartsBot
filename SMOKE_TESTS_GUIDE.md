# Smoke Tests Guide

This guide explains how to run smoke tests locally for the Felix Hub application.

## Overview

The smoke tests validate critical flows in the application:

- **Database Migrations**: Ensure migrations apply and rollback cleanly
- **API Contract Tests**: Validate API endpoints for orders, categories, and custom parts
- **E2E Smoke Tests**: Test complete user flows with mocked external services

## Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL** (optional, SQLite is used for tests by default)
3. **Dependencies installed**:
   ```bash
   pip install -r requirements.txt
   ```

## Test Structure

```
tests/
├── api/                          # API contract tests
│   ├── test_orders_api.py       # Orders CRUD and validation
│   ├── test_categories_api.py   # Categories and parts catalog
│   └── test_custom_parts_api.py # Custom parts functionality
├── e2e/                          # End-to-end tests
│   └── test_order_flow_smoke.py # Complete order flow with notifications
└── run_smoke_tests.py           # Test runner for all smoke tests

felix_hub/backend/migrations/
├── 001_add_car_number_column.py        # Car number migration
├── 002_create_categories_parts_tables.py # Categories/parts migration
└── run_migrations.py                    # Migration runner
```

## Running Tests

### 1. Run All Smoke Tests

Run the complete smoke test suite:

```bash
python tests/run_smoke_tests.py
```

This will run:
- All API contract tests
- All E2E smoke tests

### 2. Run Individual Test Suites

#### API Tests

**Orders API:**
```bash
python tests/api/test_orders_api.py
```

Tests:
- Create order with car number
- List orders
- Update order status
- Order validation (car number format, empty parts)

**Categories API:**
```bash
python tests/api/test_categories_api.py
```

Tests:
- List all categories
- List parts by category
- Get all parts

**Custom Parts API:**
```bash
python tests/api/test_custom_parts_api.py
```

Tests:
- Create order with custom parts
- Add custom part to existing order
- Verify custom parts in order list

#### E2E Tests

```bash
python tests/e2e/test_order_flow_smoke.py
```

Tests the complete flow:
1. Create order with car number and custom part
2. Verify order appears in list with correct status
3. Verify custom parts are included
4. Simulate admin status change
5. Verify Telegram notifications (mocked)

## Running Migrations

### Apply Migrations

Apply all pending migrations:

```bash
cd felix_hub/backend/migrations
python run_migrations.py apply
```

### Rollback Migrations

Rollback all migrations:

```bash
cd felix_hub/backend/migrations
python run_migrations.py rollback
```

### Check Migration Status

View available migrations:

```bash
cd felix_hub/backend/migrations
python run_migrations.py status
```

### Run Individual Migrations

**Car Number Migration:**
```bash
cd felix_hub/backend/migrations
python 001_add_car_number_column.py        # Apply
python 001_add_car_number_column.py rollback # Rollback
```

**Categories/Parts Migration:**
```bash
cd felix_hub/backend/migrations
python 002_create_categories_parts_tables.py        # Apply
python 002_create_categories_parts_tables.py rollback # Rollback
```

## Environment Variables

Set these environment variables before running tests:

```bash
export ENABLE_CAR_NUMBER=true
export ALLOW_ANY_CAR_NUMBER=false
export SECRET_KEY=test-secret-key
```

For database-connected tests (migrations):

```bash
export DATABASE_URL=postgresql://user:pass@localhost:5432/felix_hub_test
```

## CI/CD Integration

The smoke tests run automatically in CI/CD on:
- Push to `main`, `develop`, or `feat/**` branches
- Pull requests to `main` or `develop`

See `.github/workflows/ci.yml` for the CI configuration.

### CI Workflow

1. **Migration Tests**: 
   - Apply migrations
   - Check status
   - Rollback migrations
   - Re-apply migrations

2. **API Tests**: 
   - Run all API contract tests

3. **E2E Tests**: 
   - Run E2E smoke tests with mocked Telegram

4. **Full Suite**: 
   - Run complete smoke test suite

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. **For SQLite tests** (default): No action needed
2. **For PostgreSQL tests**: 
   - Ensure PostgreSQL is running
   - Check DATABASE_URL is correct
   - Create test database: `createdb felix_hub_test`

### Import Errors

If you get import errors:

```bash
# Ensure you're in the project root
cd /path/to/project

# Run tests from project root
python tests/run_smoke_tests.py
```

### Migration Already Applied

If a migration says it's already applied:

```bash
# Check current state
python run_migrations.py status

# To re-apply, first rollback
python run_migrations.py rollback
python run_migrations.py apply
```

## Test Coverage

### API Contract Tests

- ✅ Create order with car number
- ✅ Create order with custom parts
- ✅ List all orders
- ✅ Get single order details
- ✅ Update order status
- ✅ Delete order
- ✅ List categories
- ✅ List parts by category
- ✅ Get all parts
- ✅ Add custom part to order
- ✅ Validation: car number format
- ✅ Validation: empty parts
- ✅ Backward compatibility with VIN field

### E2E Smoke Tests

- ✅ Complete order flow from creation to ready
- ✅ Car number handling
- ✅ Custom parts in order
- ✅ Status updates
- ✅ Telegram notifications (mocked)
- ✅ Admin status changes

### Migration Tests

- ✅ Car number column: apply and rollback
- ✅ Categories table: create and drop
- ✅ Parts table: create and drop
- ✅ Foreign key constraints
- ✅ Indexes
- ✅ Idempotency (can run multiple times)

## Zero-Downtime Deployment

The migrations are designed for zero-downtime deployment:

1. **Additive changes**: New columns and tables are added, not removed
2. **Nullable columns**: New columns allow NULL initially
3. **Backward compatible**: Old code continues to work during deployment
4. **Rollback support**: All migrations can be rolled back if needed

### Deployment Strategy

1. Apply migrations:
   ```bash
   python felix_hub/backend/migrations/run_migrations.py apply
   ```

2. Deploy new application code

3. Verify deployment:
   ```bash
   python tests/run_smoke_tests.py
   ```

4. If issues occur, rollback:
   ```bash
   python felix_hub/backend/migrations/run_migrations.py rollback
   ```

## Best Practices

1. **Run tests before committing**: Always run smoke tests locally before pushing
2. **Check CI status**: Ensure CI passes before merging
3. **Test migrations on staging**: Test migrations on staging environment first
4. **Keep tests fast**: Smoke tests should run in under 1 minute
5. **Mock external services**: Always mock Telegram and other external services in tests
6. **Clean up test data**: Tests should clean up after themselves

## Support

For issues or questions:
- Check the [README.md](README.md) for general setup
- Review [TESTING.md](TESTING.md) for detailed testing documentation
- See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment procedures
