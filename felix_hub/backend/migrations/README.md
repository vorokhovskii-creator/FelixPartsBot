# Database Migrations

This directory contains database migration scripts for the Felix Hub application.

## Overview

Migrations are numbered sequentially (e.g., `001_`, `002_`, etc.) and can be applied or rolled back.

## Available Migrations

1. **001_add_car_number_column.py** - Adds `car_number` column to the `orders` table with an index
2. **002_create_categories_parts_tables.py** - Creates `categories` and `parts` tables with foreign keys

## Usage

### Run All Migrations

```bash
cd felix_hub/backend/migrations
python run_migrations.py apply
```

### Rollback All Migrations

```bash
cd felix_hub/backend/migrations
python run_migrations.py rollback
```

### Check Migration Status

```bash
cd felix_hub/backend/migrations
python run_migrations.py status
```

### Run Individual Migration

```bash
cd felix_hub/backend/migrations
python 001_add_car_number_column.py        # Apply
python 001_add_car_number_column.py rollback # Rollback
```

## Migration Structure

Each migration file should contain:

- `apply()` function - Applies the migration
- `rollback()` function - Rolls back the migration
- Proper error handling and idempotency checks
- Informative console output

Example:

```python
#!/usr/bin/env python3
"""
Migration 001: Description of what this migration does
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text, inspect


def apply():
    """Apply the migration"""
    with app.app_context():
        # Check if migration is already applied
        # Apply changes
        # Print success message
        return True


def rollback():
    """Rollback the migration"""
    with app.app_context():
        # Check if migration needs rollback
        # Rollback changes
        # Print success message
        return True


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback()
    else:
        apply()
```

## Best Practices

1. **Idempotency**: Migrations should be safe to run multiple times
2. **Rollback Support**: Always provide a rollback function
3. **Zero Downtime**: Design migrations for zero-downtime deployments
4. **Testing**: Test migrations in a development/staging environment first
5. **Documentation**: Document what each migration does and why

## Environment Variables

Ensure the following environment variables are set:

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Application secret key (if needed)

For PostgreSQL:
```bash
export DATABASE_URL=postgresql://user:pass@localhost:5432/felix_hub
```

For SQLite (development):
```bash
export DATABASE_URL=sqlite:///database.db
```

## Zero-Downtime Deployment

These migrations are designed for zero-downtime deployment:

1. Migrations are additive (add columns/tables, don't remove)
2. New columns are nullable initially
3. Backward compatible with existing code
4. Can be rolled back if issues occur

### Deployment Process

1. Backup database
2. Apply migrations: `python run_migrations.py apply`
3. Deploy new application code
4. Verify deployment
5. If issues occur, rollback: `python run_migrations.py rollback`

## Troubleshooting

### Migration Already Applied

If a migration says it's already applied, you can:
1. Check status: `python run_migrations.py status`
2. Rollback and re-apply if needed

### Database Connection Issues

- Verify `DATABASE_URL` is correct
- Ensure database server is running
- Check database user permissions

### Foreign Key Errors

- Ensure parent tables exist before creating child tables
- Apply migrations in order (001, 002, 003, etc.)
