"""
Evidence Analysis System for SmartDispute.ai
Handles document text extraction and AI-powered evidence analysis
"""

import os
import logging
import json
from datetime import datetime
from models import Document, Case, CaseMeritScore, db
from werkzeug.utils import secure_filename
from gemini_analyzer import analyze_evidence_with_gemini, get_enhanced_fallback_analysis

def extract_document_text(file_path, filename):
    """Extract text from uploaded documents"""
    try:
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext in ['txt']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_ext in ['pdf']:
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    return text
            except ImportError:
                logging.warning("PyPDF2 not available for PDF extraction")
                return f"Document uploaded: {filename} (text extraction not available)"
        elif file_ext in ['doc', 'docx']:
            try:
                from docx import Document as DocxDocument
                doc = DocxDocument(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                logging.warning("python-docx not available for Word document extraction")
                return f"Document uploaded: {filename} (text extraction not available)"
        else:
            return f"Document uploaded: {filename} (file type: {file_ext})"
            
    except Exception as e:
        logging.error(f"Error extracting text from {filename}: {e}")
        return f"Document uploaded: {filename} (extraction error)"

def perform_ai_evidence_analysis(processed_files, user):
    """Perform comprehensive AI analysis of uploaded evidence using OpenAI"""
    try:
        import openai
        import os
        
        # Initialize OpenAI client
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        
        # Combine all extracted text
        combined_text = ""
        document_summaries = []
        
        for file_data in processed_files:
            if file_data.get('extracted_text'):
                text = file_data['extracted_text']
                combined_text += f"Document: {file_data.get('filename', 'Unknown')}\n{text}\n\n"
                document_summaries.append({
                    'filename': file_data.get('filename', 'Unknown'),
                    'evidence_type': file_data.get('evidence_type', 'supporting'),
                    'length': len(text)
                })
        
        if not combined_text.strip():
            return get_fallback_analysis(processed_files)
        
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
        9. court_strategy: Detailed strategy for presenting this case
        10. timeline_estimate: Estimated duration for resolution
        11. cost_estimate: Estimated legal costs in CAD
        12. settlement_potential: Likelihood of out-of-court settlement (0-100)

        Focus on Canadian law, Charter rights, and practical self-representation guidance.
        """
        
        # Call OpenAI API
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a specialized Canadian legal AI assistant helping self-represented litigants."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            # Parse AI response
            response_content = response.choices[0].message.content
            if not response_content:
                logging.error("Empty response from OpenAI")
                return get_enhanced_fallback_analysis(combined_text, processed_files, user)
            
            try:
                ai_analysis = json.loads(response_content)
            except json.JSONDecodeError:
                logging.error("Failed to parse OpenAI JSON response")
                return get_enhanced_fallback_analysis(combined_text, processed_files, user)
            
            # Enhance with additional analysis
            ai_analysis.update({
                'evidence_summary': f"Analyzed {len(processed_files)} documents with {len(combined_text)} characters",
                'document_breakdown': document_summaries,
                'ai_confidence': ai_analysis.get('confidence_level', 'moderate'),
                'analysis_date': datetime.now().isoformat(),
                'disclaimer': "This AI analysis provides legal information, not legal advice. We are not lawyers. Review all analysis with qualified legal counsel."
            })
            
            return ai_analysis
            
        except json.JSONDecodeError:
            logging.error("Failed to parse OpenAI JSON response")
            return get_enhanced_fallback_analysis(combined_text, processed_files, user)
            
        except Exception as openai_error:
            logging.error(f"OpenAI API error: {openai_error}")
            return get_enhanced_fallback_analysis(combined_text, processed_files, user)
        
    except Exception as e:
        logging.error(f"Error in AI evidence analysis: {e}")
        return get_fallback_analysis(processed_files)

def get_enhanced_fallback_analysis(combined_text, processed_files, user):
    """Enhanced fallback analysis when OpenAI fails but we have document text"""
    try:
        # Determine legal issue type based on keywords
        legal_issue_type = determine_legal_issue_type(combined_text)
        
        # Extract key facts using keyword analysis
        key_facts = extract_key_facts(combined_text)
        
        # Calculate merit score based on content analysis
        merit_score = calculate_enhanced_merit_score(combined_text, legal_issue_type)
        
        # Generate recommended actions based on legal issue type
        recommended_actions = generate_fallback_actions(legal_issue_type, user)
        
        return {
            'legal_issue_type': legal_issue_type,
            'merit_score': merit_score,
            'confidence_level': 'moderate',
            'key_facts': key_facts,
            'legal_strengths': [
                "Documents uploaded and organized",
                "Clear evidence categorization",
                "Comprehensive case documentation"
            ],
            'legal_weaknesses': [
                "Full AI analysis temporarily unavailable",
                "Manual legal review recommended"
            ],
            'recommended_actions': recommended_actions,
            'relevant_laws': get_basic_relevant_laws(legal_issue_type, user),
            'court_strategy': f"Prepare for {legal_issue_type.replace('_', ' ')} proceedings with organized evidence",
            'timeline_estimate': "3-12 months depending on complexity",
            'cost_estimate': "$500-$5000 CAD for court fees and documentation",
            'settlement_potential': 60,
            'evidence_summary': f"Analyzed {len(processed_files)} documents with {len(combined_text)} characters",
            'ai_confidence': 'moderate',
            'analysis_date': datetime.now().isoformat(),
            'disclaimer': "This analysis provides legal information, not legal advice. We are not lawyers."
        }
    except Exception as e:
        logging.error(f"Enhanced fallback analysis error: {e}")
        return get_fallback_analysis(processed_files)

def get_fallback_analysis(processed_files):
    """Basic fallback when all other analysis fails"""
    return {
        'legal_issue_type': 'general',
        'merit_score': 65,
        'confidence_level': 'moderate',
        'key_facts': ["Legal documents uploaded successfully", "Case ready for review"],
        'legal_strengths': ["Complete document upload", "Organized evidence"],
        'legal_weaknesses': ["Requires legal review"],
        'recommended_actions': [
            "Review uploaded documents for completeness",
            "Consult with legal counsel if needed",
            "Prepare for court proceedings"
        ],
        'relevant_laws': ["Charter of Rights and Freedoms", "Provincial court rules"],
        'court_strategy': "Present organized evidence to court",
        'timeline_estimate': "3-6 months",
        'cost_estimate': "$1000-$3000 CAD",
        'settlement_potential': 50,
        'evidence_summary': f"Processed {len(processed_files)} documents",
        'ai_confidence': 'moderate',
        'analysis_date': datetime.now().isoformat(),
        'disclaimer': "This analysis provides legal information, not legal advice. We are not lawyers."
    }

def calculate_enhanced_merit_score(text, legal_issue_type):
    """Calculate merit score based on document content analysis"""
    score = 50  # Base score
    text_lower = text.lower()
    
    # Positive indicators
    if any(word in text_lower for word in ['evidence', 'witness', 'documentation', 'proof']):
        score += 15
    if any(word in text_lower for word in ['agreement', 'contract', 'signed', 'written']):
        score += 10
    if any(word in text_lower for word in ['violation', 'breach', 'damages', 'harm']):
        score += 10
    if len(text) > 1000:  # Substantial documentation
        score += 10
    
    # Legal issue specific scoring
    if legal_issue_type == 'family_law':
        if any(word in text_lower for word in ['best interest', 'child welfare', 'parenting']):
            score += 5
    elif legal_issue_type == 'housing_law':
        if any(word in text_lower for word in ['lease', 'notice', 'repair', 'habitability']):
            score += 5
    
    return min(85, max(30, score))  # Keep between 30-85

def generate_fallback_actions(legal_issue_type, user):
    """Generate recommended actions based on legal issue type"""
    base_actions = [
        "Organize all evidence documents",
        "Review case timeline and deadlines",
        "Prepare court filing documents"
    ]
    
    if legal_issue_type == 'family_law':
        return base_actions + [
            "File parenting plan if applicable",
            "Gather financial disclosure documents"
        ]
    elif legal_issue_type == 'housing_law':
        return base_actions + [
            "Review lease agreement terms",
            "Document property condition issues"
        ]
    elif legal_issue_type == 'employment_law':
        return base_actions + [
            "Review employment contract",
            "Document workplace incidents"
        ]
    else:
        return base_actions + [
            "Consult relevant legislation",
            "Consider alternative dispute resolution"
        ]

def get_basic_relevant_laws(legal_issue_type, user):
    """Get basic relevant laws based on legal issue type"""
    province = user.province or 'Ontario'
    
    base_laws = ["Canadian Charter of Rights and Freedoms"]
    
    if legal_issue_type == 'family_law':
        base_laws.extend([
            "Divorce Act (Canada)",
            f"Family Law Act ({province})",
            "Children's Law Reform Act"
        ])
    elif legal_issue_type == 'housing_law':
        base_laws.extend([
            f"Residential Tenancies Act ({province})",
            "Landlord and Tenant Board Rules"
        ])
    elif legal_issue_type == 'employment_law':
        base_laws.extend([
            f"Employment Standards Act ({province})",
            "Canada Labour Code"
        ])
    
    return base_laws

def determine_legal_issue_type(text):
    """Determine the type of legal issue based on document content"""
    text_lower = text.lower()
    
    if any(keyword in text_lower for keyword in ['custody', 'child', 'family', 'divorce', 'separation']):
        return 'family_law'
    elif any(keyword in text_lower for keyword in ['landlord', 'tenant', 'rent', 'eviction', 'lease']):
        return 'housing_law'
    elif any(keyword in text_lower for keyword in ['employment', 'workplace', 'fired', 'wrongful dismissal']):
        return 'employment_law'
    elif any(keyword in text_lower for keyword in ['criminal', 'charge', 'arrest', 'police']):
        return 'criminal_law'
    elif any(keyword in text_lower for keyword in ['cas', 'child protection', 'children aid society']):
        return 'child_protection'
    else:
        return 'civil_law'

def extract_key_facts(text):
    """Extract key facts from document text"""
    # Basic fact extraction - can be enhanced with NLP
    facts = []
    
    if text:
        sentences = text.split('.')
        for sentence in sentences[:10]:  # Take first 10 sentences as key facts
            if len(sentence.strip()) > 20:  # Filter out very short sentences
                facts.append(sentence.strip())
    
    if not facts:
        facts = ["Evidence documents contain relevant legal information"]
    
    return facts[:5]  # Return top 5 facts

def calculate_basic_merit_score(text, legal_issue_type):
    """Calculate a basic merit score for the case"""
    score = 50  # Base score
    
    text_lower = text.lower()
    
    # Positive indicators
    if any(keyword in text_lower for keyword in ['evidence', 'proof', 'documentation', 'witness']):
        score += 10
    if any(keyword in text_lower for keyword in ['agreement', 'contract', 'written', 'signed']):
        score += 10
    if any(keyword in text_lower for keyword in ['violation', 'breach', 'wrongful', 'illegal']):
        score += 15
    
    # Ensure score is within reasonable bounds
    return min(max(score, 20), 85)

def create_legal_case_from_evidence(analysis_result, user, processed_files):
    """Create a legal case record from analyzed evidence"""
    try:
        case = Case()
        case.user_id = user.id
        case.title = f"{analysis_result['legal_issue_type'].replace('_', ' ').title()} Case"
        case.case_type = analysis_result['legal_issue_type']
        case.merit_score = analysis_result['merit_score']
        case.status = 'analysis_complete'
        case.created_at = datetime.now()
        case.updated_at = datetime.now()
        
        # Create merit score record properly
        merit_score_record = CaseMeritScore()
        merit_score_record.score = int(analysis_result.get('merit_score', 0) * 100) if analysis_result.get('merit_score', 0) <= 1 else int(analysis_result.get('merit_score', 0))
        merit_score_record.summary = f"AI Analysis: {analysis_result.get('ai_confidence', 'medium')} confidence"
        merit_score_record.created_at = datetime.now()
        merit_score_record.details = {
            'ai_confidence': analysis_result.get('ai_confidence', 'medium'),
            'key_facts': analysis_result.get('key_facts', []),
            'analysis_date': datetime.now().isoformat(),
            'confidence_level': analysis_result.get('confidence_level', 'moderate')
        }
        
        # Store analysis metadata
        case.case_metadata = {
            'ai_analysis': analysis_result,
            'document_count': len(processed_files),
            'analysis_version': '1.0'
        }
        
        db.session.add(case)
        db.session.flush()  # Get the case ID without committing
        
        # Set the case_id for the merit score record
        merit_score_record.case_id = case.id
        db.session.add(merit_score_record)
        
        # Update documents with case_id - handle None/null document_id safely
        for file_data in processed_files:
            doc_id = file_data.get('document_id')
            if doc_id is not None:
                try:
                    document = Document.query.get(doc_id)
                    if document:
                        document.case_id = case.id
                except Exception as e:
                    logging.warning(f"Could not update document {doc_id}: {e}")
                    continue
        
        db.session.commit()
        
        return case
        
    except Exception as e:
        logging.error(f"Error creating case from evidence: {e}")
        db.session.rollback()
        raise