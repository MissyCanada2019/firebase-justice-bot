"""
SMS & Email Evidence Integration for SmartDispute.ai
Auto-scan and extract key facts from communications
"""

import os
import logging
import re
import email
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import poplib
from models import Document, Case, db
from flask_login import login_required, current_user
import json

class CommunicationAnalyzer:
    def __init__(self):
        self.evidence_patterns = {
            'threats': [
                r'(?i)\b(threat|threaten|intimidat|harass|force|coerce)\w*',
                r'(?i)\b(evict|kick out|throw out|get rid of)\b',
                r'(?i)\b(lawyer|legal action|sue|court)\b'
            ],
            'discrimination': [
                r'(?i)\b(race|religion|gender|disability|age|sexual orientation)\b',
                r'(?i)\b(discriminat|bias|prejudice|unfair treatment)\w*',
                r'(?i)\b(not wanted|not welcome|different treatment)\b'
            ],
            'financial': [
                r'\$[\d,]+\.?\d*',
                r'(?i)\b(rent|payment|deposit|fee|fine|charge)\b',
                r'(?i)\b(owe|debt|owing|balance|arrears)\b'
            ],
            'dates_deadlines': [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'(?i)\b(deadline|due date|by|before|after|until)\b',
                r'(?i)\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b'
            ],
            'maintenance_issues': [
                r'(?i)\b(repair|fix|broken|damage|leak|heat|water|electric)\w*',
                r'(?i)\b(mold|pest|noise|unsafe|hazard)\w*',
                r'(?i)\b(complaint|problem|issue|concern)\b'
            ]
        }
        
        self.communication_types = {
            'text_message': {
                'indicators': ['sent from my iphone', 'text message', 'sms'],
                'weight': 0.8
            },
            'email': {
                'indicators': ['@', 'subject:', 'from:', 'to:'],
                'weight': 0.9
            },
            'letter': {
                'indicators': ['dear', 'sincerely', 'regards', 'cc:'],
                'weight': 0.95
            },
            'voicemail': {
                'indicators': ['voicemail', 'transcript', 'audio'],
                'weight': 0.7
            }
        }

    def extract_evidence_from_text(self, text_content, communication_type='unknown'):
        """Extract legal evidence from communication text"""
        try:
            evidence = {
                'communication_type': communication_type,
                'extracted_facts': [],
                'evidence_categories': [],
                'key_dates': [],
                'financial_amounts': [],
                'participants': [],
                'urgency_level': 'normal',
                'legal_relevance': 0.0
            }
            
            # Extract evidence by category
            for category, patterns in self.evidence_patterns.items():
                matches = []
                for pattern in patterns:
                    found = re.findall(pattern, text_content)
                    matches.extend(found)
                
                if matches:
                    evidence['evidence_categories'].append(category)
                    evidence['extracted_facts'].extend(matches)
            
            # Extract specific information
            evidence['key_dates'] = self.extract_dates(text_content)
            evidence['financial_amounts'] = self.extract_financial_amounts(text_content)
            evidence['participants'] = self.extract_participants(text_content)
            
            # Calculate legal relevance score
            evidence['legal_relevance'] = self.calculate_relevance_score(evidence)
            
            # Determine urgency
            evidence['urgency_level'] = self.determine_urgency(text_content, evidence)
            
            return evidence
            
        except Exception as e:
            logging.error(f"Error extracting evidence from text: {e}")
            return None

    def extract_dates(self, text):
        """Extract dates from text"""
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            r'(?i)\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return list(set(dates))  # Remove duplicates

    def extract_financial_amounts(self, text):
        """Extract financial amounts from text"""
        amount_patterns = [
            r'\$[\d,]+\.?\d*',
            r'(?i)\b\d+\s*dollars?\b',
            r'(?i)\bCAD\s*\$?[\d,]+\.?\d*',
            r'(?i)\$[\d,]+\.?\d*\s*CAD\b'
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            amounts.extend(matches)
        
        return list(set(amounts))

    def extract_participants(self, text):
        """Extract participant names and contact information"""
        participants = []
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        participants.extend(emails)
        
        # Phone numbers
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'
        phones = re.findall(phone_pattern, text)
        participants.extend(phones)
        
        # Names (simple pattern - real names after salutations)
        name_pattern = r'(?i)(?:dear|hi|hello|from|to|cc:)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        names = re.findall(name_pattern, text)
        participants.extend(names)
        
        return list(set(participants))

    def calculate_relevance_score(self, evidence):
        """Calculate legal relevance score based on extracted evidence"""
        score = 0.0
        
        # Score by evidence categories
        category_weights = {
            'threats': 0.3,
            'discrimination': 0.35,
            'financial': 0.2,
            'dates_deadlines': 0.1,
            'maintenance_issues': 0.25
        }
        
        for category in evidence['evidence_categories']:
            score += category_weights.get(category, 0.1)
        
        # Boost for multiple types of evidence
        if len(evidence['evidence_categories']) > 2:
            score += 0.1
        
        # Boost for financial amounts
        if evidence['financial_amounts']:
            score += 0.1
        
        # Boost for specific dates
        if evidence['key_dates']:
            score += 0.05
        
        return min(1.0, score)

    def determine_urgency(self, text, evidence):
        """Determine urgency level based on content"""
        urgent_keywords = [
            'urgent', 'emergency', 'immediately', 'asap', 'deadline',
            'eviction', 'notice', 'court date', 'hearing'
        ]
        
        text_lower = text.lower()
        urgent_count = sum(1 for keyword in urgent_keywords if keyword in text_lower)
        
        if urgent_count >= 3 or 'threats' in evidence['evidence_categories']:
            return 'high'
        elif urgent_count >= 1 or evidence['key_dates']:
            return 'medium'
        else:
            return 'normal'

    def process_email_evidence(self, email_content, case_id=None):
        """Process email content for evidence extraction"""
        try:
            # Parse email
            if isinstance(email_content, str):
                msg = email.message_from_string(email_content)
            else:
                msg = email_content
            
            # Extract email metadata
            metadata = {
                'from': msg.get('From', ''),
                'to': msg.get('To', ''),
                'subject': msg.get('Subject', ''),
                'date': msg.get('Date', ''),
                'message_id': msg.get('Message-ID', '')
            }
            
            # Get email body
            body = self.extract_email_body(msg)
            
            # Extract evidence
            evidence = self.extract_evidence_from_text(body, 'email')
            evidence['metadata'] = metadata
            
            # Store as document if case_id provided
            if case_id:
                self.store_communication_evidence(case_id, evidence, 'email', body)
            
            return evidence
            
        except Exception as e:
            logging.error(f"Error processing email evidence: {e}")
            return None

    def extract_email_body(self, msg):
        """Extract text body from email message"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        return body

    def process_sms_evidence(self, sms_content, case_id=None):
        """Process SMS/text message content for evidence extraction"""
        try:
            # SMS content can be in various formats
            # Handle common formats: "From: +1234567890\nDate: 2024-01-01\nMessage: text here"
            
            sms_data = self.parse_sms_format(sms_content)
            
            # Extract evidence from message text
            evidence = self.extract_evidence_from_text(sms_data['message'], 'text_message')
            evidence['metadata'] = {
                'from': sms_data.get('from', ''),
                'to': sms_data.get('to', ''),
                'date': sms_data.get('date', ''),
                'phone_number': sms_data.get('phone_number', '')
            }
            
            # Store as document if case_id provided
            if case_id:
                self.store_communication_evidence(case_id, evidence, 'sms', sms_data['message'])
            
            return evidence
            
        except Exception as e:
            logging.error(f"Error processing SMS evidence: {e}")
            return None

    def parse_sms_format(self, sms_content):
        """Parse various SMS export formats"""
        sms_data = {
            'message': sms_content,
            'from': '',
            'to': '',
            'date': '',
            'phone_number': ''
        }
        
        # Try to extract metadata from common formats
        lines = sms_content.split('\n')
        message_start = 0
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if line_lower.startswith('from:'):
                sms_data['from'] = line.split(':', 1)[1].strip()
                message_start = max(message_start, i + 1)
            elif line_lower.startswith('to:'):
                sms_data['to'] = line.split(':', 1)[1].strip()
                message_start = max(message_start, i + 1)
            elif line_lower.startswith('date:'):
                sms_data['date'] = line.split(':', 1)[1].strip()
                message_start = max(message_start, i + 1)
            elif re.match(r'^\+?[\d\s\-\(\)]+$', line.strip()):
                sms_data['phone_number'] = line.strip()
                message_start = max(message_start, i + 1)
        
        # Extract message content (everything after metadata)
        if message_start > 0:
            sms_data['message'] = '\n'.join(lines[message_start:]).strip()
        
        return sms_data

    def store_communication_evidence(self, case_id, evidence, comm_type, content):
        """Store communication evidence as document"""
        try:
            # Create document record
            document = Document(
                case_id=case_id,
                filename=f"{comm_type}_evidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                evidence_type='supporting',  # Default to supporting evidence
                file_size=len(content.encode('utf-8')),
                upload_date=datetime.now(),
                processed=True,
                ai_analysis=json.dumps(evidence)
            )
            
            # Save content to file
            upload_dir = 'uploads'
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, document.filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            document.file_path = file_path
            
            db.session.add(document)
            db.session.commit()
            
            logging.info(f"Stored {comm_type} evidence for case {case_id}")
            return document
            
        except Exception as e:
            logging.error(f"Error storing communication evidence: {e}")
            db.session.rollback()
            return None

    def analyze_communication_thread(self, communications):
        """Analyze a thread of communications for patterns"""
        try:
            thread_analysis = {
                'total_communications': len(communications),
                'communication_types': {},
                'escalation_pattern': [],
                'key_evidence': [],
                'timeline': [],
                'overall_relevance': 0.0
            }
            
            # Sort by date
            sorted_comms = sorted(communications, key=lambda x: x.get('metadata', {}).get('date', ''))
            
            for comm in sorted_comms:
                comm_type = comm.get('communication_type', 'unknown')
                thread_analysis['communication_types'][comm_type] = thread_analysis['communication_types'].get(comm_type, 0) + 1
                
                # Track escalation
                urgency = comm.get('urgency_level', 'normal')
                thread_analysis['escalation_pattern'].append(urgency)
                
                # Collect high-relevance evidence
                if comm.get('legal_relevance', 0) > 0.6:
                    thread_analysis['key_evidence'].extend(comm.get('extracted_facts', []))
                
                # Build timeline
                timeline_entry = {
                    'date': comm.get('metadata', {}).get('date', ''),
                    'type': comm_type,
                    'urgency': urgency,
                    'relevance': comm.get('legal_relevance', 0)
                }
                thread_analysis['timeline'].append(timeline_entry)
            
            # Calculate overall relevance
            relevances = [comm.get('legal_relevance', 0) for comm in communications]
            thread_analysis['overall_relevance'] = sum(relevances) / len(relevances) if relevances else 0
            
            return thread_analysis
            
        except Exception as e:
            logging.error(f"Error analyzing communication thread: {e}")
            return None

# Global instance
communication_analyzer = CommunicationAnalyzer()

def init_communication_integration(app):
    """Initialize SMS & Email integration with Flask app"""
    @app.route('/upload-communication', methods=['POST'])
    def upload_communication():
        """Upload communication evidence (email/SMS)"""
        from flask import request, jsonify, flash, redirect, url_for
        from flask_login import login_required, current_user
        
        try:
            comm_type = request.form.get('comm_type', 'email')
            content = request.form.get('content', '')
            case_id = request.form.get('case_id')
            
            if not content:
                flash('No communication content provided', 'error')
                return redirect(url_for('upload'))
            
            # Process communication
            if comm_type == 'email':
                evidence = communication_analyzer.process_email_evidence(content, case_id)
            elif comm_type == 'sms':
                evidence = communication_analyzer.process_sms_evidence(content, case_id)
            else:
                evidence = communication_analyzer.extract_evidence_from_text(content, comm_type)
                if case_id:
                    communication_analyzer.store_communication_evidence(case_id, evidence, comm_type, content)
            
            if evidence:
                relevance = evidence.get('legal_relevance', 0)
                fact_count = len(evidence.get('extracted_facts', []))
                flash(f'Communication evidence processed! Legal relevance: {relevance*100:.0f}%, {fact_count} key facts extracted.', 'success')
                
                if case_id:
                    return redirect(url_for('case_dashboard', case_id=case_id))
            else:
                flash('Failed to process communication evidence', 'error')
            
            return redirect(url_for('upload'))
            
        except Exception as e:
            logging.error(f"Error uploading communication: {e}")
            flash(f'Error processing communication: {str(e)}', 'error')
            return redirect(url_for('upload'))
    
    @app.route('/communication-analyzer')
    @login_required
    def communication_analyzer_page():
        """Communication analyzer interface"""
        from flask import render_template
        return render_template('communication_analyzer.html')
    
    app.logger.info("SMS & Email integration initialized")
    return communication_analyzer