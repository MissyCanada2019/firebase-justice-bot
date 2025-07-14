"""
Legal Updates Dashboard for SmartDispute.ai
Displays current status of legal data scrapers and recent updates from Canadian legal sources
"""

import os
import json
import datetime
from pathlib import Path
from flask import Blueprint, render_template, jsonify, current_app, request
from flask_login import login_required, current_user
from utils.legal_data_scraper import LEGAL_SOURCES, find_documents_by_keyword, analyze_source_updates

legal_updates_bp = Blueprint('legal_updates', __name__)

@legal_updates_bp.route('/legal-updates')
@login_required
def legal_updates():
    """
    Legal updates dashboard showing scraper status and recent updates
    """
    # Get scraper status information
    last_parliament_scrape = current_app.config.get('LAST_PARLIAMENT_SCRAPE', {})
    last_legal_scrape = current_app.config.get('LAST_LEGAL_SCRAPE', {})
    last_royal_assent_check = current_app.config.get('LAST_ROYAL_ASSENT_CHECK', {})
    
    # Get recent updates from the last 7 days
    data_dir = os.path.join(current_app.root_path, 'data/legal_source_data')
    recent_updates = {}
    
    if os.path.exists(data_dir):
        try:
            recent_updates = analyze_source_updates(data_dir, days=7)
        except Exception as e:
            current_app.logger.error(f"Error analyzing recent updates: {e}")
            recent_updates = {'error': str(e)}
    
    # Calculate scraper health status
    def get_status_color(last_scrape):
        if not last_scrape or 'timestamp' not in last_scrape:
            return 'red'  # Never run
        
        try:
            last_run = datetime.datetime.fromisoformat(last_scrape['timestamp'])
            now = datetime.datetime.utcnow()
            hours_since = (now - last_run).total_seconds() / 3600
            
            if hours_since < 25:  # Within last day
                return 'green'
            elif hours_since < 48:  # Within last 2 days
                return 'yellow'
            else:
                return 'red'  # Over 2 days
        except Exception:
            return 'red'
    
    scraper_status = {
        'parliament_bills': {
            'name': 'Parliament Bills Tracker',
            'last_run': last_parliament_scrape,
            'status_color': get_status_color(last_parliament_scrape),
            'frequency': 'Daily at 2:00 AM'
        },
        'comprehensive': {
            'name': 'Comprehensive Legal Scraper',
            'last_run': last_legal_scrape,
            'status_color': get_status_color(last_legal_scrape),
            'frequency': 'Weekly on Sundays at 3:00 AM'
        },
        'royal_assent': {
            'name': 'Royal Assent Tracker',
            'last_run': last_royal_assent_check,
            'status_color': get_status_color(last_royal_assent_check),
            'frequency': 'Wednesdays & Sundays at 4:00 AM'
        }
    }
    
    return render_template('legal_updates.html',
                         scraper_status=scraper_status,
                         recent_updates=recent_updates,
                         legal_sources=LEGAL_SOURCES)

@legal_updates_bp.route('/api/search-legal-documents')
@login_required
def search_legal_documents():
    """
    API endpoint to search scraped legal documents
    """
    keyword = request.args.get('keyword', '').strip()
    max_results = min(int(request.args.get('max_results', 20)), 50)  # Cap at 50
    
    if not keyword:
        return jsonify({'error': 'Keyword is required'}), 400
    
    try:
        data_dir = os.path.join(current_app.root_path, 'data/legal_source_data')
        results = find_documents_by_keyword(keyword, data_dir, max_results)
        
        return jsonify({
            'keyword': keyword,
            'total_results': len(results),
            'documents': results
        })
    except Exception as e:
        current_app.logger.error(f"Error searching legal documents: {e}")
        return jsonify({'error': 'Search failed'}), 500

@legal_updates_bp.route('/api/trigger-scrape')
@login_required
def trigger_immediate_scrape():
    """
    API endpoint to trigger an immediate legal data scrape (admin only)
    """
    if not current_user.role or current_user.role not in ['admin', 'superadmin']:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        from utils.scheduled_tasks import run_immediate_scrape
        
        # Get requested source types
        scrape_type = request.args.get('type', 'comprehensive')  # parliament, royal_assent, or comprehensive
        
        if scrape_type == 'parliament':
            source_ids = ['parliament-bills', 'parliament-proceedings', 'senate-bills']
        elif scrape_type == 'royal_assent':
            source_ids = ['royal-assent', 'order-in-council']
        else:
            source_ids = None  # All sources
        
        # Trigger the scrape
        job_info = run_immediate_scrape(current_app, source_ids)
        
        return jsonify({
            'message': 'Scrape triggered successfully',
            'type': scrape_type,
            'job_id': job_info.get('job_id', 'unknown'),
            'status': 'started'
        })
    except Exception as e:
        current_app.logger.error(f"Error triggering immediate scrape: {e}")
        return jsonify({'error': 'Failed to trigger scrape'}), 500

@legal_updates_bp.route('/legal-source/<source_id>')
@login_required
def legal_source_details(source_id):
    """
    Display details and recent documents from a specific legal source
    """
    if source_id not in LEGAL_SOURCES:
        return "Legal source not found", 404
    
    source_info = LEGAL_SOURCES[source_id]
    
    # Get documents from this source
    data_dir = os.path.join(current_app.root_path, 'data/legal_source_data', source_id)
    documents = []
    
    if os.path.exists(data_dir):
        try:
            # Find all metadata files in the source directory
            for metadata_file in Path(data_dir).glob('*.json'):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        doc_metadata = json.load(f)
                        documents.append(doc_metadata)
                except Exception as e:
                    current_app.logger.warning(f"Error reading {metadata_file}: {e}")
            
            # Sort by date (newest first)
            documents.sort(key=lambda x: x.get('date', ''), reverse=True)
            documents = documents[:50]  # Limit to 50 most recent
            
        except Exception as e:
            current_app.logger.error(f"Error loading documents for {source_id}: {e}")
    
    return render_template('legal_source_details.html',
                         source_info=source_info,
                         source_id=source_id,
                         documents=documents)