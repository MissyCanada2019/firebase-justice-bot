"""
Create Tables Script for SmartDispute.ai

This script creates the missing tables in the database.
"""

import os
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment
DB_URL = os.environ.get('DATABASE_URL')

def run_sql(conn, sql, description="SQL command"):
    """Run a SQL command with logging and error handling"""
    cursor = conn.cursor()
    try:
        logger.info(f"Executing: {description}")
        cursor.execute(sql)
        conn.commit()
        logger.info(f"Success: {description}")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed: {description}\nError: {str(e)}")
        return False
    finally:
        cursor.close()

def create_tables():
    """Create missing tables in the database"""
    try:
        # Connect to the database
        conn = psycopg2.connect(DB_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create disputes table
        run_sql(conn, """
            CREATE TABLE IF NOT EXISTS disputes (
                id UUID PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id),
                case_type VARCHAR(100) NOT NULL DEFAULT 'general',
                status VARCHAR(50) DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                title VARCHAR(255),
                search_vector TSVECTOR
            );
        """, "Create disputes table")
        
        # Create indices for disputes table
        run_sql(conn, """
            CREATE INDEX IF NOT EXISTS ix_disputes_user_id ON disputes(user_id);
        """, "Create index on disputes.user_id")
        
        run_sql(conn, """
            CREATE INDEX IF NOT EXISTS ix_disputes_case_type ON disputes(case_type);
        """, "Create index on disputes.case_type")
        
        run_sql(conn, """
            CREATE INDEX IF NOT EXISTS ix_disputes_status ON disputes(status);
        """, "Create index on disputes.status")
        
        run_sql(conn, """
            CREATE INDEX IF NOT EXISTS ix_disputes_created_at ON disputes(created_at);
        """, "Create index on disputes.created_at")
        
        # Create case_merit_scores table
        run_sql(conn, """
            CREATE TABLE IF NOT EXISTS case_merit_scores (
                id UUID PRIMARY KEY,
                dispute_id UUID NOT NULL REFERENCES disputes(id) UNIQUE,
                score INTEGER CHECK (score >= 0 AND score <= 100),
                summary TEXT,
                legal_references TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details JSONB
            );
        """, "Create case_merit_scores table")
        
        # Create index for case_merit_scores table
        run_sql(conn, """
            CREATE INDEX IF NOT EXISTS ix_case_merit_scores_dispute_id 
            ON case_merit_scores(dispute_id);
        """, "Create index on case_merit_scores.dispute_id")
        
        # Check if we need to create chat_sessions and chat_messages tables
        run_sql(conn, """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id UUID PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id),
                dispute_id UUID REFERENCES disputes(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                title VARCHAR(200),
                session_data JSONB
            );
        """, "Create chat_sessions table")
        
        run_sql(conn, """
            CREATE INDEX IF NOT EXISTS ix_chat_sessions_user_id 
            ON chat_sessions(user_id);
        """, "Create index on chat_sessions.user_id")
        
        run_sql(conn, """
            CREATE INDEX IF NOT EXISTS ix_chat_sessions_dispute_id 
            ON chat_sessions(dispute_id);
        """, "Create index on chat_sessions.dispute_id")
        
        run_sql(conn, """
            CREATE INDEX IF NOT EXISTS ix_chat_sessions_created_at 
            ON chat_sessions(created_at);
        """, "Create index on chat_sessions.created_at")
        
        run_sql(conn, """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id UUID PRIMARY KEY,
                session_id UUID NOT NULL REFERENCES chat_sessions(id),
                is_user BOOLEAN DEFAULT TRUE,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_data JSONB
            );
        """, "Create chat_messages table")
        
        run_sql(conn, """
            CREATE INDEX IF NOT EXISTS ix_chat_messages_session_id 
            ON chat_messages(session_id);
        """, "Create index on chat_messages.session_id")
        
        run_sql(conn, """
            CREATE INDEX IF NOT EXISTS ix_chat_messages_is_user 
            ON chat_messages(is_user);
        """, "Create index on chat_messages.is_user")
        
        run_sql(conn, """
            CREATE INDEX IF NOT EXISTS ix_chat_messages_timestamp 
            ON chat_messages(timestamp);
        """, "Create index on chat_messages.timestamp")
        
        # Close the connection
        conn.close()
        logger.info("Create tables script completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Create tables script failed: {str(e)}")
        return False

if __name__ == "__main__":
    create_tables()