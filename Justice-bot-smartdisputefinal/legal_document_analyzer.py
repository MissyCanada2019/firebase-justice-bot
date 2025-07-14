"""
Advanced Legal Document Analysis and Generation System for SmartDispute.ai
Analyzes uploaded evidence to extract legal facts and generate court-ready documents
"""
import logging
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import PyPDF2
import docx
from app import db
from models import User, Case, Document, LegalReference
import openai

legal_analyzer_bp = Blueprint('legal_analyzer', __name__, url_prefix='/legal-analyzer')
logger = logging.getLogger(__name__)

# Canadian Court Levels and Jurisdictions
COURT_LEVELS = {
    'municipal': {
        'types': ['bylaw violations', 'municipal court matters', 'traffic violations', 'property tax disputes'],
        'jurisdiction': 'municipal',
        'forms': ['Notice of Violation Response', 'Municipal Court Application', 'Bylaw Challenge Form']
    },
    'provincial': {
        'types': ['small claims', 'landlord tenant', 'employment disputes', 'human rights', 'family matters', 'provincial offences'],
        'jurisdiction': 'provincial',
        'forms': ['Statement of Claim', 'Statement of Defence', 'Notice of Motion', 'Affidavit', 'Application Form']
    },
    'federal': {
        'types': ['immigration', 'tax matters', 'federal criminal', 'constitutional challenges', 'federal employment'],
        'jurisdiction': 'federal',
        'forms': ['Federal Court Application', 'Statement of Claim (Federal)', 'Notice of Constitutional Question', 'Immigration Appeal']
    }
}

# Legal Issue Categories with Charter Sections
LEGAL_CATEGORIES = {
    'housing': {
        'keywords': ['rent', 'eviction', 'landlord', 'tenant', 'lease', 'housing', 'residential'],
        'charter_sections': [7, 15],
        'legislation': ['Residential Tenancies Act', 'Human Rights Code'],
        'court_level': 'provincial'
    },
    'employment': {
        'keywords': ['employment', 'wrongful dismissal', 'workplace', 'harassment', 'discrimination', 'wages'],
        'charter_sections': [2, 7, 15],
        'legislation': ['Employment Standards Act', 'Human Rights Code', 'Labour Relations Act'],
        'court_level': 'provincial'
    },
    'human_rights': {
        'keywords': ['discrimination', 'human rights', 'equality', 'harassment', 'accommodation'],
        'charter_sections': [2, 7, 15],
        'legislation': ['Human Rights Code', 'Charter of Rights and Freedoms'],
        'court_level': 'provincial'
    },
    'criminal': {
        'keywords': ['criminal', 'charge', 'offence', 'police', 'arrest', 'bail'],
        'charter_sections': [7, 8, 9, 10, 11, 12, 13, 14, 24],
        'legislation': ['Criminal Code', 'Charter of Rights and Freedoms'],
        'court_level': 'provincial'
    },
    'immigration': {
        'keywords': ['immigration', 'refugee', 'deportation', 'visa', 'citizenship'],
        'charter_sections': [6, 7, 15],
        'legislation': ['Immigration and Refugee Protection Act', 'Citizenship Act'],
        'court_level': 'federal'
    },
    'consumer': {
        'keywords': ['consumer', 'contract', 'sale', 'warranty', 'fraud', 'unfair practice'],
        'charter_sections': [7],
        'legislation': ['Consumer Protection Act', 'Sale of Goods Act'],
        'court_level': 'provincial'
    }
}

class LegalDocumentAnalyzer:
    """
    Advanced legal document analyzer that extracts facts and generates court documents
    """
    
    def __init__(self):
        # Initialize OpenAI client only if API key is available
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            logger.info("OpenAI API key not found - AI features will be disabled")
            self.openai_client = None
    
    def extract_text_from_document(self, file_path: str, file_type: str) -> str:
        """Extract text from uploaded documents"""
        try:
            text = ""
            
            if file_type.lower() == 'pdf':
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            
            elif file_type.lower() in ['docx', 'doc']:
                doc = docx.Document(file_path)
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
            
            elif file_type.lower() == 'txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def analyze_legal_issues(self, document_text: str) -> Dict:
        """Analyze document to identify legal issues and relevant laws"""
        try:
            prompt = f"""
            Analyze this legal document/evidence and identify:
            1. Primary legal issues and categories
            2. Relevant Canadian laws and Charter sections
            3. Key facts and dates
            4. Potential legal claims or defenses
            5. Appropriate court level (municipal, provincial, federal)
            6. Urgency level and deadlines
            
            Document text:
            {document_text[:4000]}  # Limit for API
            
            Respond in JSON format with the following structure:
            {{
                "legal_issues": ["issue1", "issue2"],
                "primary_category": "category_name",
                "court_level": "provincial/federal/municipal",
                "charter_sections": [7, 15],
                "relevant_legislation": ["Act Name 1", "Act Name 2"],
                "key_facts": ["fact1", "fact2"],
                "dates": ["2023-01-01"],
                "urgency": "high/medium/low",
                "potential_claims": ["claim1", "claim2"],
                "recommended_forms": ["form1", "form2"],
                "deadline_analysis": "text about deadlines",
                "strength_assessment": "strong/moderate/weak"
            }}
            """
            
            # Use OpenAI only if client is available
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                analysis = json.loads(response.choices[0].message.content)
            else:
                # Fallback to rule-based analysis when OpenAI is not available
                analysis = self._generate_fallback_analysis(document_text)
            
            # Enhance with Canadian-specific legal knowledge
            analysis = self._enhance_with_canadian_law(analysis, document_text)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing legal issues: {e}")
            return self._get_fallback_analysis()
    
    def _enhance_with_canadian_law(self, analysis: Dict, document_text: str) -> Dict:
        """Enhance analysis with Canadian legal specifics"""
        
        # Match with predefined legal categories
        primary_category = analysis.get('primary_category', '').lower()
        
        for category, details in LEGAL_CATEGORIES.items():
            if any(keyword in document_text.lower() for keyword in details['keywords']):
                if not primary_category or category in primary_category:
                    analysis['enhanced_category'] = category
                    analysis['court_level'] = details['court_level']
                    analysis['charter_sections'] = list(set(analysis.get('charter_sections', []) + details['charter_sections']))
                    analysis['relevant_legislation'] = list(set(analysis.get('relevant_legislation', []) + details['legislation']))
                    break
        
        # Add court-specific form recommendations
        court_level = analysis.get('court_level', 'provincial')
        if court_level in COURT_LEVELS:
            analysis['available_forms'] = COURT_LEVELS[court_level]['forms']
        
        return analysis
    
    def _get_fallback_analysis(self) -> Dict:
        """Fallback analysis when AI analysis fails"""
        return {
            "legal_issues": ["General legal matter"],
            "primary_category": "general",
            "court_level": "provincial",
            "charter_sections": [7],
            "relevant_legislation": ["Charter of Rights and Freedoms"],
            "key_facts": ["Document uploaded for analysis"],
            "dates": [datetime.now().strftime('%Y-%m-%d')],
            "urgency": "medium",
            "potential_claims": ["To be determined"],
            "recommended_forms": ["Statement of Claim"],
            "deadline_analysis": "Please consult with legal counsel for specific deadlines",
            "strength_assessment": "requires_review"
        }
    
    def generate_court_document(self, case_id: int, document_type: str, analysis: Dict) -> str:
        """Generate court-ready documents based on analysis"""
        try:
            case = Case.query.get(case_id)
            if not case:
                raise ValueError("Case not found")
            
            # Get case documents and evidence
            documents = Document.query.filter_by(case_id=case_id).all()
            evidence_text = "\n".join([doc.extracted_text or "" for doc in documents if doc.extracted_text])
            
            court_level = analysis.get('court_level', 'provincial')
            legal_issues = analysis.get('legal_issues', [])
            charter_sections = analysis.get('charter_sections', [])
            
            prompt = f"""
            Generate a professional, court-ready {document_type} for Canadian {court_level} court.
            
            Case Information:
            - Case Title: {case.title}
            - Legal Issues: {', '.join(legal_issues)}
            - Court Level: {court_level}
            - Charter Sections: {charter_sections}
            
            Legal Analysis:
            {json.dumps(analysis, indent=2)}
            
            Evidence Summary:
            {evidence_text[:2000]}
            
            Requirements:
            1. Follow proper Canadian court formatting
            2. Include all required legal elements
            3. Reference relevant Charter sections and legislation
            4. Use formal legal language
            5. Include proper court filing information
            6. Ensure document is ready for immediate filing
            
            Generate a complete, professional {document_type} that meets all Canadian court standards.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating court document: {e}")
            return self._generate_fallback_document(document_type, case)
    
    def _generate_fallback_document(self, document_type: str, case) -> str:
        """Generate a basic template when AI generation fails"""
        return f"""
        COURT FILE NO: [TO BE ASSIGNED]
        
        ONTARIO
        SUPERIOR COURT OF JUSTICE
        
        BETWEEN:
        
        {case.user.first_name} {case.user.last_name}
        - Applicant/Plaintiff
        
        AND:
        
        [RESPONDENT NAME]
        - Respondent/Defendant
        
        {document_type.upper()}
        
        TO THE HONOURABLE COURT:
        
        1. This application/claim relates to: {case.title}
        
        2. The facts giving rise to this matter are as follows:
           [Facts to be inserted based on evidence analysis]
        
        3. The legal grounds for this application are:
           [Legal grounds to be specified]
        
        4. The relief sought is:
           [Relief to be specified]
        
        DATED at [CITY], Ontario, this [DAY] day of [MONTH], [YEAR].
        
        ________________________________
        {case.user.first_name} {case.user.last_name}
        Applicant/Plaintiff
        [ADDRESS]
        [PHONE]
        [EMAIL]
        
        Note: This is a template document. Professional legal review is recommended before filing.
        """

# Initialize analyzer
legal_analyzer = LegalDocumentAnalyzer()

@legal_analyzer_bp.route('/analyze-document/<int:document_id>')
@login_required
def analyze_document(document_id):
    """Analyze a specific document for legal issues"""
    try:
        document = Document.query.filter_by(id=document_id, user_id=current_user.id).first()
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Extract text if not already done
        if not document.extracted_text and document.file_path:
            document.extracted_text = legal_analyzer.extract_text_from_document(
                document.file_path, document.file_type
            )
            db.session.commit()
        
        # Analyze legal issues
        analysis = legal_analyzer.analyze_legal_issues(document.extracted_text or "")
        
        # Store analysis in document metadata
        if not document.doc_metadata:
            document.doc_metadata = {}
        document.doc_metadata['legal_analysis'] = analysis
        document.doc_metadata['analysis_date'] = datetime.utcnow().isoformat()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'document_id': document_id
        })
        
    except Exception as e:
        logger.error(f"Error analyzing document {document_id}: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@legal_analyzer_bp.route('/analyze-case/<int:case_id>')
@login_required
def analyze_case(case_id):
    """Analyze all documents in a case for comprehensive legal assessment"""
    try:
        case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        documents = Document.query.filter_by(case_id=case_id).all()
        
        # Combine all document texts
        combined_text = ""
        analyses = []
        
        for doc in documents:
            if not doc.extracted_text and doc.file_path:
                doc.extracted_text = legal_analyzer.extract_text_from_document(
                    doc.file_path, doc.file_type
                )
            
            if doc.extracted_text:
                combined_text += doc.extracted_text + "\n\n"
                
                # Get individual document analysis
                doc_analysis = legal_analyzer.analyze_legal_issues(doc.extracted_text)
                analyses.append(doc_analysis)
        
        # Comprehensive case analysis
        case_analysis = legal_analyzer.analyze_legal_issues(combined_text)
        
        # Store in case metadata
        if not case.case_metadata:
            case.case_metadata = {}
        case.case_metadata['comprehensive_analysis'] = case_analysis
        case.case_metadata['document_analyses'] = analyses
        case.case_metadata['analysis_date'] = datetime.utcnow().isoformat()
        
        # Update case type based on analysis
        if case_analysis.get('primary_category'):
            case.case_type = case_analysis['primary_category']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'case_analysis': case_analysis,
            'document_analyses': analyses,
            'case_id': case_id
        })
        
    except Exception as e:
        logger.error(f"Error analyzing case {case_id}: {e}")
        return jsonify({'error': 'Case analysis failed'}), 500

@legal_analyzer_bp.route('/generate-document/<int:case_id>')
@login_required
def generate_document_form(case_id):
    """Show form to generate court documents"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
    if not case:
        return "Case not found", 404
    
    analysis = case.case_metadata.get('comprehensive_analysis', {}) if case.case_metadata else {}
    court_level = analysis.get('court_level', 'provincial')
    available_forms = COURT_LEVELS.get(court_level, {}).get('forms', [])
    
    return render_template('legal_analyzer/generate_document.html', 
                         case=case, analysis=analysis, available_forms=available_forms)

@legal_analyzer_bp.route('/generate-document/<int:case_id>', methods=['POST'])
@login_required
def generate_document(case_id):
    """Generate a specific court document"""
    try:
        case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        document_type = request.json.get('document_type')
        if not document_type:
            return jsonify({'error': 'Document type required'}), 400
        
        # Get case analysis
        analysis = case.case_metadata.get('comprehensive_analysis', {}) if case.case_metadata else {}
        
        if not analysis:
            return jsonify({'error': 'Case must be analyzed first'}), 400
        
        # Generate document
        document_content = legal_analyzer.generate_court_document(case_id, document_type, analysis)
        
        # Create generated form record
        from models import GeneratedForm
        generated_form = GeneratedForm(
            case_id=case_id,
            user_id=current_user.id,
            form_type=document_type,
            form_title=f"{document_type} - {case.title}",
            generated_file_path=f"generated/{case_id}_{document_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            is_paid=False,  # Mark as free for testing
            created_at=datetime.utcnow(),
            form_data={'content': document_content, 'analysis': analysis}
        )
        
        db.session.add(generated_form)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'document_content': document_content,
            'form_id': generated_form.id,
            'download_url': f'/download-form/{generated_form.id}'
        })
        
    except Exception as e:
        logger.error(f"Error generating document for case {case_id}: {e}")
        return jsonify({'error': 'Document generation failed'}), 500

@legal_analyzer_bp.route('/legal-research/<int:case_id>')
@login_required
def legal_research(case_id):
    """Provide relevant legal research and precedents for a case"""
    try:
        case = Case.query.filter_by(id=case_id, user_id=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        analysis = case.case_metadata.get('comprehensive_analysis', {}) if case.case_metadata else {}
        
        # Find relevant legal references
        legal_issues = analysis.get('legal_issues', [])
        charter_sections = analysis.get('charter_sections', [])
        
        relevant_references = []
        
        # Search for relevant legal references
        for issue in legal_issues:
            refs = LegalReference.query.filter(
                LegalReference.title.ilike(f'%{issue}%')
            ).limit(3).all()
            relevant_references.extend([ref.to_dict() for ref in refs])
        
        # Add Charter references
        for section in charter_sections:
            charter_refs = LegalReference.query.filter(
                LegalReference.citation.ilike(f'%section {section}%')
            ).limit(2).all()
            relevant_references.extend([ref.to_dict() for ref in charter_refs])
        
        return jsonify({
            'success': True,
            'legal_research': {
                'relevant_references': relevant_references,
                'charter_sections': charter_sections,
                'legal_issues': legal_issues,
                'recommended_reading': analysis.get('relevant_legislation', [])
            }
        })
        
    except Exception as e:
        logger.error(f"Error conducting legal research for case {case_id}: {e}")
        return jsonify({'error': 'Legal research failed'}), 500

def init_legal_analyzer(app):
    """Initialize legal document analyzer with Flask app"""
    app.register_blueprint(legal_analyzer_bp)
    logger.info("Legal document analyzer initialized")