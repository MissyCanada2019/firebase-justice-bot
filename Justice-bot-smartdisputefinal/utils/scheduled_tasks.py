"""
Scheduled Tasks for SmartDispute.ai

This module handles automatic background tasks such as:
- Weekly legal data scraping from various Canadian legal sources
- Email notifications about new legal updates
- Database maintenance and cleanup

Tasks run on a predefined schedule using APScheduler.
"""

import os
import logging
import datetime
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None

def initialize_scheduler(app):
    """
    Initialize the background task scheduler with the Flask app context
    
    Args:
        app: Flask application instance
    """
    global scheduler
    
    if scheduler is None:
        logger.info("Initializing background task scheduler")
        scheduler = BackgroundScheduler()
        
        # Critical legal scraper will be added after function definition
        
        # Schedule daily Parliament bills (2:00 AM)
        scheduler.add_job(
            func=run_parliament_bills_scraper,
            trigger=CronTrigger(hour=2, minute=0),
            id='daily_parliament_scraper',
            max_instances=1,
            replace_existing=True,
            args=[app]
        )
        
        # Schedule Royal Assent tracking (daily at 3:00 AM)
        scheduler.add_job(
            func=run_royal_assent_tracker,
            trigger=CronTrigger(hour=3, minute=0),
            id='daily_royal_assent_tracker',
            max_instances=1,
            replace_existing=True,
            args=[app]
        )
        
        # Schedule comprehensive legal data scraping (Sundays at 4:00 AM)
        scheduler.add_job(
            func=run_legal_data_scraper,
            trigger=CronTrigger(day_of_week='sun', hour=4, minute=0),
            id='weekly_legal_scraper',
            max_instances=1,
            replace_existing=True,
            args=[app]
        )
        
        # Schedule daily database optimization (Every day at 3:00 AM)
        scheduler.add_job(
            func=run_database_maintenance,
            trigger=CronTrigger(hour=3, minute=0),
            id='daily_db_maintenance',
            max_instances=1,
            replace_existing=True,
            args=[app]
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info("Background task scheduler started successfully")


def run_parliament_bills_scraper(app):
    """
    Run specialized Parliament bills scraper daily to track new legislation
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        try:
            logger.info("Starting daily Parliament bills scraper")
            
            from utils.legal_data_scraper import LegalDataScraper
            
            data_dir = os.path.join(app.root_path, 'data/legal_source_data')
            os.makedirs(data_dir, exist_ok=True)
            
            scraper = LegalDataScraper(data_dir=data_dir)
            
            # Focus on Parliament-specific sources
            parliament_sources = ['parliament-bills', 'parliament-proceedings', 'senate-bills', 'royal-assent']
            
            def run_parliament_scraper():
                try:
                    summary = scraper.run_targeted_scrape(parliament_sources)
                    logger.info(f"Parliament bills scrape completed: {summary['total_documents']} documents")
                    
                    app.config['LAST_PARLIAMENT_SCRAPE'] = {
                        'timestamp': datetime.datetime.utcnow().isoformat(),
                        'summary': summary
                    }
                    
                except Exception as e:
                    logger.error(f"Error in Parliament scraper: {e}")
            
            scraper_thread = threading.Thread(target=run_parliament_scraper)
            scraper_thread.daemon = True
            scraper_thread.start()
            
        except Exception as e:
            logger.error(f"Parliament bills scraper failed: {e}")


def run_royal_assent_tracker(app):
    """
    Track Royal Assent for new laws becoming effective
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        try:
            logger.info("Starting Royal Assent tracker")
            
            from utils.legal_data_scraper import LegalDataScraper
            
            data_dir = os.path.join(app.root_path, 'data/legal_source_data')
            os.makedirs(data_dir, exist_ok=True)
            
            scraper = LegalDataScraper(data_dir=data_dir)
            
            def run_royal_assent_check():
                try:
                    # Focus on Royal Assent and Orders in Council
                    sources = ['royal-assent', 'order-in-council']
                    summary = scraper.run_targeted_scrape(sources)
                    
                    logger.info(f"Royal Assent tracking completed: {summary['total_documents']} new laws tracked")
                    
                    app.config['LAST_ROYAL_ASSENT_CHECK'] = {
                        'timestamp': datetime.datetime.utcnow().isoformat(),
                        'summary': summary
                    }
                    
                except Exception as e:
                    logger.error(f"Error in Royal Assent tracker: {e}")
            
            tracker_thread = threading.Thread(target=run_royal_assent_check)
            tracker_thread.daemon = True
            tracker_thread.start()
            
        except Exception as e:
            logger.error(f"Royal Assent tracker failed: {e}")


def run_critical_legal_scraper(app):
    """
    Run daily scraper for critical legal areas: Family Law, Criminal Law, and CAS/Child Protection
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        try:
            logger.info("Starting daily critical legal areas scraper")
            
            from utils.legal_data_scraper import LegalDataScraper
            
            data_dir = os.path.join(app.root_path, 'data/legal_source_data')
            os.makedirs(data_dir, exist_ok=True)
            
            scraper = LegalDataScraper(data_dir=data_dir)
            
            # Critical legal areas requiring daily updates
            critical_sources = [
                # Criminal Law
                'criminal-code', 'criminal-cases-scc', 'canlii-criminal', 'youth-criminal-justice',
                'controlled-drugs-substances', 'criminal-lawyers-association',
                
                # Family Law
                'divorce-act', 'family-orders-enforcement', 'ontario-family-law', 
                'ontario-children-law-reform', 'bc-family-law', 'quebec-civil-code-family',
                'alberta-family-law', 'family-court-decisions', 'family-law-central',
                'domestic-violence-resources', 'legal-aid-ontario',
                
                # CAS and Child Protection
                'child-family-services-act-ontario', 'bc-child-family-community-service',
                'alberta-child-youth-family-enhancement', 'quebec-youth-protection',
                'saskatchewan-child-family-services', 'manitoba-child-family-services',
                'nova-scotia-children-family-services', 'new-brunswick-family-services',
                'pei-child-protection', 'newfoundland-children-youth-families',
                'ontario-cas-websites', 'child-welfare-information-gateway'
            ]
            
            def run_critical_scraper():
                try:
                    summary = scraper.run_targeted_scrape(critical_sources)
                    logger.info(f"Critical legal scrape completed: {summary['total_documents']} documents")
                    
                    app.config['LAST_CRITICAL_LEGAL_SCRAPE'] = {
                        'timestamp': datetime.datetime.utcnow().isoformat(),
                        'summary': summary
                    }
                    
                except Exception as e:
                    logger.error(f"Error in critical legal scraper: {e}")
            
            scraper_thread = threading.Thread(target=run_critical_scraper)
            scraper_thread.daemon = True
            scraper_thread.start()
            
        except Exception as e:
            logger.error(f"Critical legal scraper failed: {e}")


def add_critical_scraper_job(app):
    """Add the critical legal scraper job after all functions are defined"""
    global scheduler
    if scheduler and scheduler.running:
        try:
            scheduler.add_job(
                func=run_critical_legal_scraper,
                trigger=CronTrigger(hour=1, minute=0),
                id='daily_critical_legal_scraper',
                max_instances=1,
                replace_existing=True,
                args=[app]
            )
            logger.info("Critical legal scraper job added successfully")
        except Exception as e:
            logger.warning(f"Could not add critical legal scraper: {e}")


def run_legal_data_scraper(app):
    """
    Run the legal data scraper with the Flask app context
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        try:
            logger.info("Starting scheduled legal data scrape")
            
            # Import the legal data scraper
            from utils.legal_data_scraper import LegalDataScraper
            
            # Create data directory
            data_dir = os.path.join(app.root_path, 'data/legal_source_data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Initialize and run the scraper
            scraper = LegalDataScraper(data_dir=data_dir)
            
            # Run the scraper in a background thread to avoid blocking
            def run_scraper_thread():
                try:
                    summary = scraper.run_scheduled_scrape()
                    logger.info(f"Weekly legal scrape completed: {summary['total_documents']} documents from {summary['sources_scraped']} sources")
                    
                    # Store the last scrape information
                    app.config['LAST_LEGAL_SCRAPE'] = {
                        'timestamp': datetime.datetime.utcnow().isoformat(),
                        'summary': summary
                    }
                    
                    # Send notification to admins about the scrape results
                    send_scrape_notification(app, summary)
                    
                except Exception as e:
                    logger.error(f"Error running legal scraper: {str(e)}")
            
            # Start the scraper thread
            thread = threading.Thread(target=run_scraper_thread)
            thread.daemon = True
            thread.start()
            
            logger.info("Legal data scrape thread started")
            
        except Exception as e:
            logger.error(f"Error in scheduled legal scrape: {str(e)}")


def send_scrape_notification(app, summary):
    """
    Send email notification to admins about the legal scrape results
    
    Args:
        app: Flask application instance
        summary: Scrape summary data
    """
    try:
        # Import email utility
        from flask import render_template_string
        
        # Get admin users
        from models import User
        admin_users = User.query.filter_by(role='admin').all()
        
        if not admin_users:
            logger.warning("No admin users found for scrape notification")
            return
        
        # Simple email template
        email_template = """
        <h2>Weekly Legal Data Scrape Completed</h2>
        <p>The weekly legal data scrape has been completed successfully.</p>
        
        <h3>Summary:</h3>
        <ul>
            <li>Total documents: {{ summary.total_documents }}</li>
            <li>Sources scraped: {{ summary.sources_scraped }}</li>
            <li>Duration: {{ "%.2f"|format(summary.duration_seconds / 60) }} minutes</li>
        </ul>
        
        <h3>Documents by Source:</h3>
        <ul>
        {% for source, count in summary.documents_by_source.items() %}
            <li>{{ source }}: {{ count }}</li>
        {% endfor %}
        </ul>
        
        <p>View the latest legal updates on the <a href="{{ url }}">Legal Updates</a> page.</p>
        """
        
        # Render the email content
        from flask import url_for
        legal_updates_url = url_for('legal_updates', _external=True)
        email_content = render_template_string(
            email_template, 
            summary=summary, 
            url=legal_updates_url
        )
        
        # Send the email to each admin
        for admin in admin_users:
            # Check if we have a send_email function
            if hasattr(app, 'send_email'):
                app.send_email(
                    subject="SmartDispute.ai - Weekly Legal Scrape Completed",
                    recipient=admin.email,
                    html_content=email_content
                )
            else:
                logger.warning("Email sending not configured - notification skipped")
        
        logger.info(f"Sent scrape notifications to {len(admin_users)} admin users")
        
    except Exception as e:
        logger.error(f"Error sending scrape notification: {str(e)}")


def run_database_maintenance(app):
    """
    Perform routine database maintenance and optimization
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        try:
            logger.info("Starting scheduled database maintenance")
            
            # Get SQLAlchemy engine from app
            engine = app.extensions['sqlalchemy'].db.engine
            
            # Run VACUUM ANALYZE
            with engine.connect() as conn:
                # Turn off auto-commit mode for maintenance operations
                conn.execute("VACUUM ANALYZE;")
                
            logger.info("Database maintenance completed successfully")
            
        except Exception as e:
            logger.error(f"Error in database maintenance: {str(e)}")


def shutdown_scheduler():
    """
    Shutdown the background task scheduler
    """
    global scheduler
    
    if scheduler and scheduler.running:
        logger.info("Shutting down background task scheduler")
        scheduler.shutdown()
        scheduler = None


def run_immediate_scrape(app, source_ids=None):
    """
    Run an immediate legal data scrape for specific or all sources
    
    Args:
        app: Flask application instance
        source_ids: List of source IDs to scrape, or None for all sources
        
    Returns:
        dict: Job information
    """
    with app.app_context():
        try:
            # Import the legal data scraper
            from utils.legal_data_scraper import LegalDataScraper, LEGAL_SOURCES
            
            # Validate source IDs
            if source_ids:
                invalid_ids = [sid for sid in source_ids if sid not in LEGAL_SOURCES]
                if invalid_ids:
                    return {
                        'success': False,
                        'error': f"Invalid source IDs: {', '.join(invalid_ids)}"
                    }
            
            # Create data directory
            data_dir = os.path.join(app.root_path, 'data/legal_source_data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Initialize the scraper
            scraper = LegalDataScraper(data_dir=data_dir)
            
            # Define the job function
            def scrape_job():
                try:
                    if source_ids:
                        # Scrape specific sources
                        results = {}
                        for source_id in source_ids:
                            try:
                                logger.info(f"Scraping source: {LEGAL_SOURCES[source_id]['name']}")
                                source_results = scraper.scrape_source(source_id)
                                results[source_id] = source_results
                                logger.info(f"Completed scraping {LEGAL_SOURCES[source_id]['name']}: {len(source_results)} documents")
                            except Exception as e:
                                logger.error(f"Error scraping {LEGAL_SOURCES[source_id]['name']}: {e}")
                                results[source_id] = []
                                
                        # Create a summary
                        summary = {
                            'started_at': datetime.datetime.utcnow().isoformat(),
                            'completed_at': datetime.datetime.utcnow().isoformat(),
                            'sources_scraped': len(results),
                            'total_documents': sum(len(docs) for docs in results.values()),
                            'documents_by_source': {
                                source_id: len(docs) for source_id, docs in results.items()
                            }
                        }
                    else:
                        # Scrape all sources
                        summary = scraper.run_scheduled_scrape()
                    
                    logger.info(f"Immediate scrape completed: {summary['total_documents']} documents")
                    
                    # Store the last scrape information
                    app.config['LAST_LEGAL_SCRAPE'] = {
                        'timestamp': datetime.datetime.utcnow().isoformat(),
                        'summary': summary
                    }
                    
                except Exception as e:
                    logger.error(f"Error in immediate scrape job: {str(e)}")
            
            # Run the job in a background thread
            thread = threading.Thread(target=scrape_job)
            thread.daemon = True
            thread.start()
            
            # Return success
            sources_desc = f"sources: {', '.join(source_ids)}" if source_ids else "all sources"
            return {
                'success': True,
                'message': f"Started immediate scrape of {sources_desc}",
                'timestamp': datetime.datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error starting immediate scrape: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


def get_scheduler_status():
    """
    Get the status of the background task scheduler
    
    Returns:
        dict: Scheduler status information
    """
    global scheduler
    
    if not scheduler:
        return {
            'running': False,
            'message': 'Scheduler not initialized'
        }
    
    jobs = []
    for job in scheduler.get_jobs():
        next_run = job.next_run_time.isoformat() if job.next_run_time else None
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': next_run
        })
    
    return {
        'running': scheduler.running,
        'jobs': jobs
    }