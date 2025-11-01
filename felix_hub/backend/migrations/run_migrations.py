#!/usr/bin/env python3
"""
Migration runner script
Runs all pending migrations or rolls them back.
"""

import sys
import os
import importlib.util

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_migration_files():
    """Get all migration files sorted by number"""
    migrations_dir = os.path.dirname(os.path.abspath(__file__))
    files = []
    
    for filename in os.listdir(migrations_dir):
        if filename.endswith('.py') and filename[0].isdigit():
            files.append(filename)
    
    return sorted(files)


def load_migration(filepath):
    """Load a migration module dynamically"""
    spec = importlib.util.spec_from_file_location("migration", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_migrations(rollback=False):
    """Run all migrations or rollback"""
    migrations_dir = os.path.dirname(os.path.abspath(__file__))
    migration_files = get_migration_files()
    
    if not migration_files:
        print("No migrations found.")
        return True
    
    action = "Rolling back" if rollback else "Applying"
    print(f"\n{action} migrations...")
    print("=" * 50)
    
    # Reverse order for rollback
    if rollback:
        migration_files = list(reversed(migration_files))
    
    success_count = 0
    fail_count = 0
    
    for filename in migration_files:
        filepath = os.path.join(migrations_dir, filename)
        print(f"\n{action} {filename}...")
        
        try:
            migration = load_migration(filepath)
            
            if rollback:
                if hasattr(migration, 'rollback'):
                    result = migration.rollback()
                else:
                    print(f"⚠️  No rollback function found in {filename}")
                    result = True
            else:
                if hasattr(migration, 'apply'):
                    result = migration.apply()
                else:
                    print(f"❌ No apply function found in {filename}")
                    result = False
            
            if result:
                success_count += 1
            else:
                fail_count += 1
                print(f"❌ Failed to {action.lower()} {filename}")
        
        except Exception as e:
            fail_count += 1
            print(f"❌ Error {action.lower()} {filename}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"✅ Successfully {action.lower()} {success_count} migration(s)")
    if fail_count > 0:
        print(f"❌ Failed to {action.lower()} {fail_count} migration(s)")
        return False
    
    return True


def show_status():
    """Show migration status"""
    migration_files = get_migration_files()
    
    print("\nAvailable migrations:")
    print("=" * 50)
    
    for filename in migration_files:
        print(f"  - {filename}")
    
    print(f"\nTotal: {len(migration_files)} migration(s)")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'rollback':
            success = run_migrations(rollback=True)
            sys.exit(0 if success else 1)
        elif command == 'status':
            show_status()
            sys.exit(0)
        elif command == 'apply':
            success = run_migrations(rollback=False)
            sys.exit(0 if success else 1)
        else:
            print("Usage: python run_migrations.py [apply|rollback|status]")
            print("  apply    - Apply all pending migrations (default)")
            print("  rollback - Rollback all migrations")
            print("  status   - Show migration status")
            sys.exit(1)
    else:
        # Default action is to apply migrations
        success = run_migrations(rollback=False)
        sys.exit(0 if success else 1)
