# SmartDispute.ai Database Migration Guide

This document provides instructions for migrating the SmartDispute.ai database to the new UUID-based schema.

## Overview

We are migrating from the old schema with integer primary keys to a new schema using UUIDs for several benefits:
- Improved security (IDs aren't sequential or predictable)
- Better distributed systems support
- Simplified data merging/synchronization 
- Future-proofing for scalability

## Migration Options

Choose one of the following options depending on your needs:

### Option 1: Clean Setup (Recommended for Development/Testing)

This option completely rebuilds the database with the new schema. **All existing data will be deleted**.

```bash
# Option 1A: Run the Python script (with a confirmation prompt)
python db_setup.py

# Option 1B: Use the SQL script directly
psql -U your_user -d your_database -f setup_database.sql
```

### Option 2: Data Migration (For Production)

This option attempts to preserve existing data by migrating it to the new schema.

```bash
# First take a database backup!
pg_dump -U your_user -d your_database > backup_before_migration.sql

# Then run the migration script
python db_uuid_migration.py
```

## Post-Migration Steps

After migration, verify that:

1. All tables are using the new UUID-based schema
2. Data has been properly migrated (if using Option 2)
3. The application works properly with the new schema

## Troubleshooting

If you encounter issues during migration:

- Check the migration script logs for errors
- Verify that all tables have been created correctly
- For Option 2, check that the data has been properly mapped between old and new schemas
- If all else fails, restore from backup and try again

## Schema Overview

The new database schema includes these main tables:

1. `users` - User accounts and profiles
2. `disputes` - Main case information (formerly called "cases")
3. `documents` - Files associated with disputes
4. `payments` - Payment records
5. `case_merit_scores` - Analysis scores and summaries for disputes
6. `chat_sessions` - User chat session data
7. `chat_messages` - Individual chat messages

For more details, see the database schema documentation or explore the `models.py` file.

## Known Issues

- Migration of complex relationships (many-to-many) may require manual verification
- Some application features might need minor updates to work with UUIDs
- Search functions have been optimized for the new schema

## Need Help?

Contact the development team at smartdisputecanada@gmail.com for assistance.