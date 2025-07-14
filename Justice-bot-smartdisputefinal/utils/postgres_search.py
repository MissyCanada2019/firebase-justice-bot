"""
PostgreSQL Full-Text Search Utilities

This module provides utilities for working with PostgreSQL's full-text search capabilities.
"""

from sqlalchemy import text
from app import db
from models import Case, Document, LegalIssue
import logging

# Configure logging
logger = logging.getLogger(__name__)

def update_search_vectors():
    """Update search vectors for all models that support full-text search"""
    try:
        with db.engine.connect() as conn:
            # Start a transaction
            transaction = conn.begin()
            
            try:
                # Update Case search vectors
                conn.execute(text('''
                UPDATE cases
                SET search_vector = 
                    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(category, '')), 'B') ||
                    setweight(to_tsvector('english', COALESCE(status, '')), 'C')
                WHERE search_vector IS NULL OR 
                      title IS NOT NULL OR
                      category IS NOT NULL OR
                      status IS NOT NULL
                '''))
                
                # Update Document search vectors
                conn.execute(text('''
                UPDATE documents
                SET search_vector = 
                    setweight(to_tsvector('english', COALESCE(filename, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(file_type, '')), 'B') ||
                    setweight(to_tsvector('english', COALESCE(extracted_text, '')), 'C')
                WHERE search_vector IS NULL OR 
                      filename IS NOT NULL OR
                      file_type IS NOT NULL OR
                      extracted_text IS NOT NULL
                '''))
                
                # Update LegalIssue search vectors if table exists
                if 'legal_issues' in db.inspect(db.engine).get_table_names():
                    conn.execute(text('''
                    UPDATE legal_issues
                    SET search_vector = 
                        setweight(to_tsvector('english', COALESCE(issue_type, '')), 'A') ||
                        setweight(to_tsvector('english', COALESCE(category, '')), 'B') ||
                        setweight(to_tsvector('english', COALESCE(description, '')), 'C')
                    WHERE search_vector IS NULL OR 
                          issue_type IS NOT NULL OR
                          category IS NOT NULL OR
                          description IS NOT NULL
                    '''))
                
                # Commit the transaction
                transaction.commit()
                logger.info("Successfully updated search vectors")
                return True
            
            except Exception as e:
                transaction.rollback()
                logger.error(f"Error updating search vectors: {e}")
                return False
    
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False


def search_cases(query, user_id=None, limit=10):
    """
    Search cases using PostgreSQL full-text search
    
    Args:
        query (str): Search query
        user_id (int, optional): Limit to cases owned by this user
        limit (int, optional): Maximum number of results
        
    Returns:
        list: List of matching Case objects
    """
    try:
        # Create the base query
        search_query = Case.query.filter(
            Case.search_vector.match(query)
        ).order_by(
            text("ts_rank(search_vector, to_tsquery('english', :query)) DESC")
        ).params(query=query)
        
        # Add user filter if specified
        if user_id is not None:
            search_query = search_query.filter(Case.user_id == user_id)
        
        return search_query.limit(limit).all()
    
    except Exception as e:
        logger.error(f"Error searching cases: {e}")
        return []


def search_documents(query, user_id=None, case_id=None, limit=10):
    """
    Search documents using PostgreSQL full-text search
    
    Args:
        query (str): Search query
        user_id (int, optional): Limit to documents owned by this user
        case_id (int, optional): Limit to documents in this case
        limit (int, optional): Maximum number of results
        
    Returns:
        list: List of matching Document objects
    """
    try:
        # Create the base query
        search_query = Document.query.filter(
            Document.search_vector.match(query)
        ).order_by(
            text("ts_rank(search_vector, to_tsquery('english', :query)) DESC")
        ).params(query=query)
        
        # Add filters if specified
        if user_id is not None:
            search_query = search_query.filter(Document.user_id == user_id)
        
        if case_id is not None:
            search_query = search_query.filter(Document.case_id == case_id)
        
        return search_query.limit(limit).all()
    
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return []


def search_legal_issues(query, category=None, limit=10):
    """
    Search legal issues using PostgreSQL full-text search
    
    Args:
        query (str): Search query
        category (str, optional): Limit to issues in this category
        limit (int, optional): Maximum number of results
        
    Returns:
        list: List of matching LegalIssue objects
    """
    try:
        # Make sure the legal_issues table exists
        if 'legal_issues' not in db.inspect(db.engine).get_table_names():
            logger.warning("legal_issues table does not exist")
            return []
        
        # Create the base query
        search_query = LegalIssue.query.filter(
            LegalIssue.search_vector.match(query)
        ).order_by(
            text("ts_rank(search_vector, to_tsquery('english', :query)) DESC")
        ).params(query=query)
        
        # Add category filter if specified
        if category is not None:
            search_query = search_query.filter(LegalIssue.category == category)
        
        return search_query.limit(limit).all()
    
    except Exception as e:
        logger.error(f"Error searching legal issues: {e}")
        return []


# Trigger function to automatically update search vectors on insert/update
def create_trigger_functions():
    """Create PostgreSQL trigger functions to automatically update search vectors"""
    try:
        with db.engine.connect() as conn:
            # Start a transaction
            transaction = conn.begin()
            
            try:
                # Create function for cases
                conn.execute(text('''
                CREATE OR REPLACE FUNCTION cases_search_vector_update() RETURNS trigger AS $$
                BEGIN
                    NEW.search_vector :=
                        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                        setweight(to_tsvector('english', COALESCE(NEW.category, '')), 'B') ||
                        setweight(to_tsvector('english', COALESCE(NEW.status, '')), 'C');
                    RETURN NEW;
                END
                $$ LANGUAGE plpgsql;
                '''))
                
                # Create function for documents
                conn.execute(text('''
                CREATE OR REPLACE FUNCTION documents_search_vector_update() RETURNS trigger AS $$
                BEGIN
                    NEW.search_vector :=
                        setweight(to_tsvector('english', COALESCE(NEW.filename, '')), 'A') ||
                        setweight(to_tsvector('english', COALESCE(NEW.file_type, '')), 'B') ||
                        setweight(to_tsvector('english', COALESCE(NEW.extracted_text, '')), 'C');
                    RETURN NEW;
                END
                $$ LANGUAGE plpgsql;
                '''))
                
                # Create function for legal_issues if table exists
                if 'legal_issues' in db.inspect(db.engine).get_table_names():
                    conn.execute(text('''
                    CREATE OR REPLACE FUNCTION legal_issues_search_vector_update() RETURNS trigger AS $$
                    BEGIN
                        NEW.search_vector :=
                            setweight(to_tsvector('english', COALESCE(NEW.issue_type, '')), 'A') ||
                            setweight(to_tsvector('english', COALESCE(NEW.category, '')), 'B') ||
                            setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'C');
                        RETURN NEW;
                    END
                    $$ LANGUAGE plpgsql;
                    '''))
                
                # Commit the transaction
                transaction.commit()
                logger.info("Successfully created trigger functions")
                return True
            
            except Exception as e:
                transaction.rollback()
                logger.error(f"Error creating trigger functions: {e}")
                return False
    
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False


def create_search_triggers():
    """Create PostgreSQL triggers to automatically update search vectors"""
    try:
        with db.engine.connect() as conn:
            # Start a transaction
            transaction = conn.begin()
            
            try:
                # Drop existing triggers if they exist
                conn.execute(text('DROP TRIGGER IF EXISTS cases_search_update ON cases'))
                conn.execute(text('DROP TRIGGER IF EXISTS documents_search_update ON documents'))
                if 'legal_issues' in db.inspect(db.engine).get_table_names():
                    conn.execute(text('DROP TRIGGER IF EXISTS legal_issues_search_update ON legal_issues'))
                
                # Create trigger for cases
                conn.execute(text('''
                CREATE TRIGGER cases_search_update
                BEFORE INSERT OR UPDATE OF title, category, status
                ON cases
                FOR EACH ROW
                EXECUTE FUNCTION cases_search_vector_update();
                '''))
                
                # Create trigger for documents
                conn.execute(text('''
                CREATE TRIGGER documents_search_update
                BEFORE INSERT OR UPDATE OF filename, file_type, extracted_text
                ON documents
                FOR EACH ROW
                EXECUTE FUNCTION documents_search_vector_update();
                '''))
                
                # Create trigger for legal_issues if table exists
                if 'legal_issues' in db.inspect(db.engine).get_table_names():
                    conn.execute(text('''
                    CREATE TRIGGER legal_issues_search_update
                    BEFORE INSERT OR UPDATE OF issue_type, category, description
                    ON legal_issues
                    FOR EACH ROW
                    EXECUTE FUNCTION legal_issues_search_vector_update();
                    '''))
                
                # Commit the transaction
                transaction.commit()
                logger.info("Successfully created search triggers")
                return True
            
            except Exception as e:
                transaction.rollback()
                logger.error(f"Error creating search triggers: {e}")
                return False
    
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False


def setup_full_text_search():
    """Setup full-text search for PostgreSQL"""
    # Create trigger functions
    if not create_trigger_functions():
        logger.error("Failed to create trigger functions")
        return False
    
    # Create triggers
    if not create_search_triggers():
        logger.error("Failed to create triggers")
        return False
    
    # Update existing search vectors
    if not update_search_vectors():
        logger.error("Failed to update search vectors")
        return False
    
    logger.info("Successfully set up PostgreSQL full-text search")
    return True