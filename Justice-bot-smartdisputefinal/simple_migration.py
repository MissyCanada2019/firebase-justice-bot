import os
import logging
import psycopg2
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get database URL from environment
db_url = os.environ.get("DATABASE_URL")

# Parse database connection parameters
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://')

# Parse connection details from URL
# Example: postgresql://user:password@host:port/database
conn_details = {}
if '://' in db_url:
    # Extract credentials and hostname
    auth_url = db_url.split('://', 1)[1]
    if '@' in auth_url:
        auth, host_part = auth_url.split('@', 1)
        if ':' in auth:
            conn_details['user'], conn_details['password'] = auth.split(':', 1)
        else:
            conn_details['user'] = auth
        
        # Extract host, port, and database name
        if '/' in host_part:
            host_and_port, db_name = host_part.split('/', 1)
            conn_details['dbname'] = db_name.split('?', 1)[0]  # Remove query params if any
            
            if ':' in host_and_port:
                conn_details['host'], conn_details['port'] = host_and_port.split(':', 1)
            else:
                conn_details['host'] = host_and_port
else:
    # Use environment variables directly if available
    conn_details = {
        'host': os.environ.get('PGHOST'),
        'port': os.environ.get('PGPORT'),
        'dbname': os.environ.get('PGDATABASE'),
        'user': os.environ.get('PGUSER'),
        'password': os.environ.get('PGPASSWORD')
    }
    # Remove None values
    conn_details = {k: v for k, v in conn_details.items() if v is not None}

def check_table_exists(conn, table_name):
    """Check if a table exists in the database"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            )
        """, (table_name,))
        return cur.fetchone()[0]

def count_rows(conn, table_name):
    """Count rows in a table"""
    with conn.cursor() as cur:
        cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        return cur.fetchone()[0]

def get_table_columns(conn, table_name):
    """Get column names for a table"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s
        """, (table_name,))
        return {row[0]: row[1] for row in cur.fetchall()}

def migrate_user_to_users(conn):
    """Migrate data from 'user' table to 'users' table"""
    if not check_table_exists(conn, 'user'):
        logger.info("Old 'user' table doesn't exist, skipping migration")
        return
    
    if not check_table_exists(conn, 'users'):
        logger.info("New 'users' table doesn't exist, skipping migration")
        return
    
    # Get column mapping between tables
    user_columns = get_table_columns(conn, 'user')
    users_columns = get_table_columns(conn, 'users')
    
    # Find common columns
    common_columns = set(user_columns.keys()) & set(users_columns.keys())
    
    # Always exclude these columns
    exclude_columns = {'id'}
    common_columns = common_columns - exclude_columns
    
    logger.info(f"Common columns between 'user' and 'users': {common_columns}")
    logger.info(f"All columns in 'users' table: {list(users_columns.keys())}")
    
    # Count rows for logging
    old_count = count_rows(conn, 'user')
    new_count = count_rows(conn, 'users')
    logger.info(f"Found {old_count} records in old 'user' table and {new_count} in new 'users' table")
    
    if old_count == 0:
        logger.info("No data to migrate from 'user' table")
        return
    
    try:
        with conn.cursor() as cur:
            # Get emails and usernames from users table
            cur.execute("SELECT email FROM users")
            existing_emails = {row[0] for row in cur.fetchall()}
            
            cur.execute("SELECT username FROM users")
            existing_usernames = {row[0] for row in cur.fetchall()}
            
            # Get records from old table
            cur.execute(f'SELECT {", ".join(common_columns)} FROM "user"')
            old_records = cur.fetchall()
            
            # Prepare column string and placeholders for INSERT
            # Add uuid column which is required and full_name column
            all_columns = list(common_columns) + ['uuid', 'full_name']
            columns_str = ", ".join(all_columns)
            placeholders = ", ".join(["%s"] * len(all_columns))
            
            # Insert records that don't exist in new table
            migrated = 0
            for record in old_records:
                # Create dict of column name to value
                record_dict = dict(zip(common_columns, record))
                
                # Skip if email already exists
                if 'email' in record_dict and record_dict['email'] in existing_emails:
                    logger.info(f"User with email {record_dict['email']} already exists, skipping")
                    continue
                
                # Check and fix username if it already exists
                if 'username' in record_dict and record_dict['username'] in existing_usernames:
                    old_username = record_dict['username']
                    new_username = f"{old_username}_{uuid.uuid4().hex[:6]}"
                    logger.info(f"Username {old_username} already exists, changing to {new_username}")
                    record_dict['username'] = new_username
                
                # Add a UUID for each user and set full_name from username
                values = [record_dict[col] for col in common_columns]
                values.append(str(uuid.uuid4()))  # Add a random UUID
                values.append(record_dict.get('username', 'User'))  # Set full_name to username or default
                
                # Insert the record
                cur.execute(
                    f'INSERT INTO users ({columns_str}) VALUES ({placeholders})',
                    tuple(values)
                )
                migrated += 1
            
            conn.commit()
            logger.info(f"Successfully migrated {migrated} users from 'user' to 'users'")
            
    except Exception as e:
        conn.rollback()
        logger.error(f"Error migrating users: {e}")
        raise

def migrate_case_to_cases(conn):
    """Migrate data from 'case' table to 'cases' table"""
    if not check_table_exists(conn, 'case'):
        logger.info("Old 'case' table doesn't exist, skipping migration")
        return
    
    if not check_table_exists(conn, 'cases'):
        logger.info("New 'cases' table doesn't exist, skipping migration")
        return
    
    # Get column mapping between tables
    case_columns = get_table_columns(conn, 'case')
    cases_columns = get_table_columns(conn, 'cases')
    
    # Find common columns
    common_columns = set(case_columns.keys()) & set(cases_columns.keys())
    
    # Always exclude these columns
    exclude_columns = {'id'}
    common_columns = common_columns - exclude_columns
    
    # Handle column renaming from category -> case_type
    column_mapping = {}
    if 'category' in case_columns and 'case_type' in cases_columns and 'category' not in common_columns:
        common_columns.discard('category')  # Remove if present
        column_mapping['category'] = 'case_type'
    
    logger.info(f"Common columns between 'case' and 'cases': {common_columns}")
    logger.info(f"Column mappings: {column_mapping}")
    
    # Count rows for logging
    old_count = count_rows(conn, 'case')
    new_count = count_rows(conn, 'cases')
    logger.info(f"Found {old_count} records in old 'case' table and {new_count} in new 'cases' table")
    
    if old_count == 0:
        logger.info("No data to migrate from 'case' table")
        return
    
    try:
        with conn.cursor() as cur:
            # Get records from old table
            select_columns = list(common_columns)
            for old_col in column_mapping:
                if old_col not in select_columns:
                    select_columns.append(old_col)
            
            cur.execute(f'SELECT id, {", ".join(select_columns)} FROM "case"')
            old_records = cur.fetchall()
            
            # Prepare columns for insert
            insert_columns = list(common_columns)
            for old_col, new_col in column_mapping.items():
                if new_col not in insert_columns:
                    insert_columns.append(new_col)
            
            columns_str = ", ".join(insert_columns)
            placeholders = ", ".join(["%s"] * len(insert_columns))
            
            # Track successfully migrated cases for document updates
            migrated_case_ids = {}
            
            # Insert records
            migrated = 0
            for record in old_records:
                old_id = record[0]  # First column is id
                record = record[1:]  # Skip id for remaining columns
                
                # Create dict of column name to value
                record_dict = dict(zip(select_columns, record))
                
                # Apply column mappings
                insert_values = []
                for col in insert_columns:
                    if col in record_dict:
                        insert_values.append(record_dict[col])
                    elif col in column_mapping.values():
                        # Find old column name
                        old_col = next(k for k, v in column_mapping.items() if v == col)
                        insert_values.append(record_dict.get(old_col))
                    else:
                        insert_values.append(None)
                
                # Insert and get the new ID
                cur.execute(
                    f'INSERT INTO cases ({columns_str}) VALUES ({placeholders}) RETURNING id',
                    tuple(insert_values)
                )
                new_id = cur.fetchone()[0]
                migrated_case_ids[old_id] = new_id
                migrated += 1
            
            # Update documents to point to new case IDs
            if migrated_case_ids and check_table_exists(conn, 'documents'):
                logger.info(f"Updating document references to point to new case IDs")
                for old_id, new_id in migrated_case_ids.items():
                    cur.execute(
                        'UPDATE documents SET case_id = %s WHERE case_id = %s',
                        (new_id, old_id)
                    )
            
            conn.commit()
            logger.info(f"Successfully migrated {migrated} cases from 'case' to 'cases'")
            
    except Exception as e:
        conn.rollback()
        logger.error(f"Error migrating cases: {e}")
        raise

def drop_old_tables(conn):
    """Drop old tables after migration"""
    try:
        with conn.cursor() as cur:
            for table in ['user', 'case']:
                if check_table_exists(conn, table):
                    logger.info(f"Dropping old '{table}' table")
                    cur.execute(f'DROP TABLE IF EXISTS "{table}"')
            conn.commit()
            logger.info("Successfully dropped old tables")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error dropping old tables: {e}")
        raise

def main():
    """Run the migration"""
    try:
        logger.info(f"Connecting to database with parameters: {conn_details}")
        conn = psycopg2.connect(**conn_details)
        
        try:
            migrate_user_to_users(conn)
            migrate_case_to_cases(conn)
            
            # Skip dropping tables for now due to foreign key constraints
            logger.info("Skipping dropping old tables due to foreign key constraints")
            logger.info("Migration of data completed successfully")
            logger.info("NOTE: Old tables 'user' and 'case' still exist but data has been migrated to new tables 'users' and 'cases'")
            
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
    return True

if __name__ == "__main__":
    main()