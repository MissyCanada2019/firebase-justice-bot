"""
Evidence Analysis System for SmartDispute.ai
Handles document text extraction and AI-powered evidence analysis with Canadian legal focus
"""

import os
import logging
import json
from datetime import datetime
from models import Document, Case, CaseMeritScore, db
from werkzeug.utils import secure_filename
from gemini_analyzer import analyze_evidence_with_gemini, get_enhanced_fallback_analysis

def extract_text_from_file(file_path):
    """Extract text content from various file types"""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        elif file_extension == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    return text
            except Exception:
                logging.warning(f"Failed to extract PDF text from {file_path}")
                return ""
        elif file_extension in ['.docx', '.doc']:
            try:
                from docx import Document
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except Exception:
                logging.warning(f"Failed to extract Word document text from {file_path}")
                return ""
        else:
            logging.warning(f"Unsupported file type: {file_extension}")
            return ""
    except Exception as e:
        logging.error(f"Error extracting text from {file_path}: {str(e)}")
        return ""

def analyze_evidence(processed_files, user):
    """
    Comprehensive Canadian legal evidence analysis using multiple AI providers
    """
    try:
        # Extract text from all uploaded documents
        combined_text = ""
        document_summaries = []
        
        for file_info in processed_files:
            if 'file_path' in file_info:
                text = extract_text_from_file(file_info['file_path'])
                combined_text += f"\n\n--- Document: {file_info.get('filename', 'Unknown')} ---\n{text}"
                
                document_summaries.append({
                    'filename': file_info.get('filename', 'Unknown'),
                    'evidence_type': file_info.get('evidence_type', 'supporting'),
                    'word_count': len(text.split()) if text else 0,
                    'status': 'processed' if text else 'failed'
                })
        
        if not combined_text.strip():
            return get_enhanced_fallback_analysis(combined_text, processed_files, user)
        
        # Try Gemini first, then OpenAI, then fallback
        logging.info("Attempting Canadian legal analysis...")
        
        # First try Google Gemini (free tier available)
        try:
            ai_analysis = analyze_evidence_with_gemini(combined_text, processed_files, user)
            if ai_analysis and ai_analysis.get('ai_provider') == 'Google Gemini':
                logging.info("Successfully completed Gemini analysis")
                ai_analysis['document_breakdown'] = document_summaries
                return ai_analysis
        except Exception as gemini_error:
            logging.warning(f"Gemini analysis failed: {gemini_error}")
        
        # Try OpenAI as backup
        try:
            from openai import OpenAI
            
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                client = OpenAI(api_key=api_key)
                
                system_prompt = f"""You are a Canadian legal AI assistant specializing in Canadian federal and provincial law.

Analyze the following legal documents for a case in {getattr(user, 'province', 'Ontario')}, Canada.

Focus on:
- Canadian Charter of Rights and Freedoms
- Provincial laws for {getattr(user, 'province', 'Ontario')}
- Federal statutes (Criminal Code, Family Law, etc.)
- Municipal bylaws where applicable
- Self-representation strategies for Canadian courts

Provide analysis in JSON format with these fields:
- merit_score: Integer 0-100
- confidence_level: "high", "moderate", or "low"
- key_facts: Array of key facts
- legal_strengths: Array of strengths
- legal_weaknesses: Array of weaknesses  
- recommended_actions: Array of next steps
- relevant_laws: Array of applicable Canadian laws
- timeline_estimate: String
- cost_estimate: String
- settlement_potential: "high", "moderate", or "low"

IMPORTANT: JSON only, no extra text."""

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Canadian Legal Analysis: {combined_text[:8000]}"}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=2000,
                    temperature=0.3
                )
                
                if response.choices[0].message.content:
                    ai_analysis = json.loads(response.choices[0].message.content)
                    ai_analysis.update({
                        'evidence_summary': f"Analyzed {len(processed_files)} documents",
                        'document_breakdown': document_summaries,
                        'ai_provider': 'OpenAI GPT-4',
                        'analysis_date': datetime.now().isoformat(),
                        'disclaimer': "This AI analysis provides Canadian legal information, not legal advice."
                    })
                    logging.info("Successfully completed OpenAI analysis")
                    return ai_analysis
                    
        except Exception as openai_error:
            logging.warning(f"OpenAI analysis failed: {openai_error}")
        
        # Use enhanced fallback
        logging.info("Using enhanced Canadian legal fallback analysis")
        ai_analysis = get_enhanced_fallback_analysis(combined_text, processed_files, user)
        ai_analysis['document_breakdown'] = document_summaries
        return ai_analysis
        
    except Exception as e:
        logging.error(f"Error in evidence analysis: {str(e)}")
        return get_enhanced_fallback_analysis("", processed_files, user)

def create_case_from_analysis(user, ai_analysis, processed_files):
    """Create a legal case record from analyzed evidence"""
    try:
        # Create new case
        case = Case(
            user_id=user.id,
            case_title=f"Legal Matter - {datetime.now().strftime('%Y-%m-%d')}",
            case_type=ai_analysis.get('legal_issue_type', 'General Legal Matter'),
            status='under_review',
            created_at=datetime.now()
        )
        
        db.session.add(case)
        db.session.flush()  # Get case ID
        
        # Create merit score record
        merit_score_record = CaseMeritScore(
            case_id=case.id,
            merit_score=ai_analysis.get('merit_score', 50),
            confidence_level=ai_analysis.get('confidence_level', 'moderate'),
            key_facts=json.dumps(ai_analysis.get('key_facts', [])),
            legal_strengths=json.dumps(ai_analysis.get('legal_strengths', [])),
            legal_weaknesses=json.dumps(ai_analysis.get('legal_weaknesses', [])),
            recommended_actions=json.dumps(ai_analysis.get('recommended_actions', [])),
            created_at=datetime.now()
        )
        
        db.session.add(merit_score_record)
        
        # Link documents to case
        for file_info in processed_files:
            if 'document_id' in file_info:
                document = Document.query.get(file_info['document_id'])
                if document:
                    document.case_id = case.id
        
        db.session.commit()
        logging.info(f"Created case {case.id} with merit score {merit_score_record.merit_score}")
        
        return case
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating case from analysis: {str(e)}")
        raise

def extract_document_text(file_path):
    """Extract text from document - alias for extract_text_from_file"""
    return extract_text_from_file(file_path)

def perform_ai_evidence_analysis(processed_files, user):
    """Perform AI evidence analysis - alias for analyze_evidence"""
    return analyze_evidence(processed_files, user)

def create_legal_case_from_evidence(user, ai_analysis, processed_files):
    """Create legal case from evidence - alias for create_case_from_analysis"""
    return create_case_from_analysis(user, ai_analysis, processed_files)

def init_evidence_analyzer(app):
    """Initialize the evidence analyzer with the Flask app"""
    app.logger.info("Evidence analyzer initialized")