# Deployment Checklist - Migrations and Smoke Tests

Use this checklist when deploying the migrations and smoke tests implementation.

## Pre-Deployment

### 1. Code Review
- [ ] Review all migration scripts
- [ ] Review all test files
- [ ] Review CI/CD configuration
- [ ] Review documentation

### 2. Local Testing
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run all smoke tests: `python tests/run_smoke_tests.py`
- [ ] Test migrations apply: `python felix_hub/backend/migrations/run_migrations.py apply`
- [ ] Test migrations rollback: `python felix_hub/backend/migrations/run_migrations.py rollback`
- [ ] Re-apply migrations: `python felix_hub/backend/migrations/run_migrations.py apply`
- [ ] All tests pass locally

### 3. Staging Environment
- [ ] Deploy to staging environment
- [ ] Run migrations on staging: `python felix_hub/backend/migrations/run_migrations.py apply`
- [ ] Run smoke tests on staging: `python tests/run_smoke_tests.py`
- [ ] Verify API endpoints work correctly
- [ ] Test order creation with car number and custom parts
- [ ] Test status updates
- [ ] Verify database schema matches expected structure

### 4. CI/CD Verification
- [ ] Push to feature branch
- [ ] Verify GitHub Actions workflow runs successfully
- [ ] All CI tests pass
- [ ] Migration tests pass
- [ ] API contract tests pass
- [ ] E2E smoke tests pass

## Deployment Steps

### 1. Backup Database
```bash
# For PostgreSQL
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql

# For Railway/Render, use their backup tools
```

### 2. Apply Migrations
```bash
cd felix_hub/backend/migrations
python run_migrations.py apply
```

Expected output:
```
Applying migrations...
==================================================

Applying 001_add_car_number_column.py...
✅ Migration 001 applied successfully!
   - Added car_number column (VARCHAR(20))
   - Created index idx_orders_car_number

Applying 002_create_categories_parts_tables.py...
✅ Migration 002 applied successfully!

==================================================
✅ Successfully applied 2 migration(s)
```

### 3. Verify Migrations
```bash
python run_migrations.py status
```

### 4. Deploy Application Code
```bash
# Push to main branch (triggers automatic deployment)
git push origin feat/migrations-smoke-tests-orders-notifications:main

# Or deploy manually depending on your setup
```

### 5. Run Smoke Tests (Post-Deployment)
```bash
# Set environment variables for production
export DATABASE_URL=$PRODUCTION_DATABASE_URL
export SECRET_KEY=$PRODUCTION_SECRET_KEY
export ENABLE_CAR_NUMBER=true

# Run smoke tests
python tests/run_smoke_tests.py
```

### 6. Verify Functionality
- [ ] Create a test order with car number
- [ ] Create a test order with custom parts
- [ ] Update order status
- [ ] Verify notifications work
- [ ] Check admin panel
- [ ] Verify category/parts endpoints

## Post-Deployment Monitoring

### 1. Application Health
- [ ] Check application logs for errors
- [ ] Monitor response times
- [ ] Verify no 500 errors

### 2. Database Health
- [ ] Check database connection pool
- [ ] Monitor query performance
- [ ] Verify indexes are being used

### 3. API Endpoints
- [ ] Test `POST /api/orders` with car number
- [ ] Test `GET /api/orders`
- [ ] Test `PATCH /api/orders/:id`
- [ ] Test `GET /api/categories`
- [ ] Test `GET /api/parts`

### 4. CI/CD
- [ ] Verify CI runs successfully on main branch
- [ ] Check that tests pass in CI
- [ ] Monitor for any flaky tests

## Rollback Procedure (If Needed)

If issues are detected:

### 1. Stop Taking New Orders (Optional)
- [ ] Set maintenance mode if available
- [ ] Or disable order creation temporarily

### 2. Rollback Application Code
```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or rollback deployment in hosting platform
```

### 3. Rollback Migrations (If Necessary)
```bash
cd felix_hub/backend/migrations
python run_migrations.py rollback
```

### 4. Verify Rollback
- [ ] Test application functionality
- [ ] Run smoke tests
- [ ] Check database schema
- [ ] Verify no data loss

### 5. Restore Database Backup (If Necessary)
```bash
# For PostgreSQL
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < backup_file.sql
```

## Success Criteria

- [ ] All migrations applied successfully
- [ ] Application deployed without errors
- [ ] All smoke tests pass
- [ ] No increase in error rates
- [ ] API response times normal
- [ ] Database queries performing well
- [ ] CI/CD pipeline green
- [ ] No customer-reported issues

## Communication

### Before Deployment
- [ ] Notify team of deployment schedule
- [ ] Alert on-call engineers
- [ ] Update status page (if applicable)

### After Deployment
- [ ] Announce successful deployment
- [ ] Document any issues encountered
- [ ] Update deployment log
- [ ] Share metrics/results with team

## Troubleshooting

### Migration Fails
- Check database connection
- Verify database permissions
- Review migration logs
- Check if column/table already exists
- Rollback and retry

### Tests Fail
- Check environment variables
- Verify database is accessible
- Review test logs
- Check for flaky tests
- Verify Telegram bot token (for production)

### Application Errors
- Review application logs
- Check database queries
- Verify API endpoints
- Test with curl/Postman
- Check network connectivity

## Additional Resources

- [SMOKE_TESTS_GUIDE.md](SMOKE_TESTS_GUIDE.md) - How to run tests locally
- [MIGRATIONS_SMOKE_TESTS_SUMMARY.md](MIGRATIONS_SMOKE_TESTS_SUMMARY.md) - Implementation overview
- [felix_hub/backend/migrations/README.md](felix_hub/backend/migrations/README.md) - Migration documentation
- [.github/workflows/ci.yml](.github/workflows/ci.yml) - CI configuration

## Contact

For issues or questions during deployment:
- Check documentation first
- Review error logs
- Contact development team
- Create incident ticket if needed

---

**Remember:** Test thoroughly in staging before deploying to production!
