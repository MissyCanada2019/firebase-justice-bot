"""
Case management routes for Justice-Bot
Document upload, AI analysis, and case tracking
"""

import os
import uuid
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify, send_file
from flask_login import login_required, current_user
from models import Case, Document, db
from services.ai_service import analyze_legal_case, calculate_merit_score
from services.doc_service import extract_text_from_file

cases_bp = Blueprint('cases', __name__)

ALLOWED_EXTENSIONS = {'txt', 'docx', 'pdf', 'doc', 'jpg', 'jpeg', 'png', 'tiff', 'bmp', 'gif'}

def allowed_file(filename):
    """Check if uploaded file type is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_available_forms(case):
    """Determine available forms based on case type and analysis"""
    forms = []
    
    # Basic forms available for all cases with merit score >= 40
    if case.merit_score and case.merit_score >= 40:
        forms.extend([
            {'name': 'Application to Court', 'type': 'application', 'icon': 'fas fa-gavel'},
            {'name': 'Affidavit', 'type': 'affidavit', 'icon': 'fas fa-scroll'},
            {'name': 'Motion Record', 'type': 'motion', 'icon': 'fas fa-file-contract'},
            {'name': 'Factum', 'type': 'factum', 'icon': 'fas fa-clipboard-list'}
        ])
    
    # Add specific forms based on case type
    if case.legal_issue_type:
        if 'family' in case.legal_issue_type.lower():
            forms.extend([
                {'name': 'Financial Statement', 'type': 'financial_statement', 'icon': 'fas fa-dollar-sign'},
                {'name': 'Parenting Plan', 'type': 'parenting_plan', 'icon': 'fas fa-users'}
            ])
        elif 'tenant' in case.legal_issue_type.lower() or 'landlord' in case.legal_issue_type.lower():
            forms.append({'name': 'LTB Application', 'type': 'ltb_application', 'icon': 'fas fa-home'})
        elif 'employment' in case.legal_issue_type.lower():
            forms.append({'name': 'Employment Standards Claim', 'type': 'employment_claim', 'icon': 'fas fa-briefcase'})
        elif 'cas' in case.legal_issue_type.lower() or 'child_protection' in case.legal_issue_type.lower():
            forms.extend([
                {'name': 'CAS Response', 'type': 'cas_response', 'icon': 'fas fa-shield-alt'},
                {'name': 'Access Request', 'type': 'access_request', 'icon': 'fas fa-child'}
            ])
    
    return forms

@cases_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_case():
    """Create new case with document upload"""
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        legal_issue_type = request.form.get('legal_issue_type', '')
        
        # Validation
        if not title or len(title) < 5:
            flash("Please provide a descriptive case title (at least 5 characters)", 'error')
            return render_template('cases/new.html')
        
        if not description or len(description) < 20:
            flash("Please provide a detailed case description (at least 20 characters)", 'error')
            return render_template('cases/new.html')
        
        if not legal_issue_type:
            flash("Please select the type of legal issue", 'error')
            return render_template('cases/new.html')
        
        try:
            # Create new case
            case = Case(
                user_id=current_user.id,
                title=title,
                description=description,
                legal_issue_type=legal_issue_type,
                status='draft'
            )
            
            db.session.add(case)
            db.session.flush()  # Get the case ID
            
            # Handle file upload if provided
            uploaded_file = request.files.get('evidence_file')
            if uploaded_file and uploaded_file.filename and allowed_file(uploaded_file.filename):
                # Save uploaded file
                filename = secure_filename(uploaded_file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                uploaded_file.save(file_path)
                
                # Extract text content
                extracted_text = extract_text_from_file(file_path, uploaded_file.content_type)
                
                # Create document record
                document = Document(
                    case_id=case.id,
                    filename=unique_filename,
                    original_filename=filename,
                    file_path=file_path,
                    file_size=os.path.getsize(file_path),
                    content_type=uploaded_file.content_type,
                    document_type='evidence',
                    extracted_text=extracted_text
                )
                
                db.session.add(document)
                
                # Combine description and extracted text for analysis
                full_text = f"{description}\n\n{extracted_text}" if extracted_text else description
            else:
                full_text = description
            
            # Run AI analysis
            try:
                ai_analysis = analyze_legal_case(full_text, legal_issue_type)
                merit_score = calculate_merit_score(full_text, legal_issue_type, ai_analysis)
                
                # Update case with AI results
                case.classification = ai_analysis.get('classification', legal_issue_type)
                case.merit_score = merit_score
                case.ai_summary = ai_analysis.get('summary', '')
                case.recommended_actions = ai_analysis.get('recommendations', '')
                case.status = 'analyzed'
                case.analyzed_at = datetime.utcnow()
                
            except Exception as e:
                current_app.logger.error(f"AI analysis failed: {e}")
                # Continue without AI analysis
                case.merit_score = 50  # Default neutral score
                case.classification = legal_issue_type
                flash("Case created successfully. AI analysis will be available shortly.", 'warning')
            
            db.session.commit()
            
            flash("Your case has been created and analyzed successfully!", 'success')
            return redirect(url_for('cases.view_case', case_id=case.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating case: {e}")
            flash("An error occurred while creating your case. Please try again.", 'error')
    
    return render_template('cases/new.html')

@cases_bp.route('/<int:case_id>')
@login_required
def view_case(case_id):
    """View individual case details with comprehensive AI analysis"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    documents = case.documents.all()
    
    # Parse AI analysis data
    if case.ai_analysis:
        try:
            import json
            if isinstance(case.ai_analysis, str):
                case.ai_analysis = json.loads(case.ai_analysis)
        except:
            pass
    
    # Parse recommended actions if they exist
    if case.recommended_actions:
        try:
            import json
            if isinstance(case.recommended_actions, str):
                case.recommended_actions = json.loads(case.recommended_actions)
        except:
            # If parsing fails, convert string to list
            if isinstance(case.recommended_actions, str):
                case.recommended_actions = [case.recommended_actions]
    
    # Parse legal pathways from AI analysis or generate based on case type
    legal_pathways = []
    
    # Try to get from AI analysis first
    try:
        if case.ai_analysis:
            import json
            ai_data = json.loads(case.ai_analysis) if isinstance(case.ai_analysis, str) else case.ai_analysis
            legal_pathways = ai_data.get('legal_pathways', [])
    except:
        pass
    
    # If no pathways from AI, generate based on case type and merit score
    if not legal_pathways and case.merit_score:
        if 'family' in case.legal_issue_type.lower():
            legal_pathways = [
                {'name': 'Court Application', 'description': 'File formal application for custody/access', 
                 'merit_score': case.merit_score, 'timeframe': '2-4 months'},
                {'name': 'Mediation', 'description': 'Attempt mediated settlement with other party', 
                 'merit_score': min(case.merit_score + 10, 100), 'timeframe': '1-2 months'},
                {'name': 'Emergency Motion', 'description': 'Urgent court motion if children at risk', 
                 'merit_score': case.merit_score - 10 if case.merit_score > 60 else 40, 'timeframe': '1-2 weeks'}
            ]
        elif 'employment' in case.legal_issue_type.lower():
            legal_pathways = [
                {'name': 'Employment Standards Claim', 'description': 'File with Ministry of Labour', 
                 'merit_score': case.merit_score, 'timeframe': '3-6 months'},
                {'name': 'Small Claims Court', 'description': 'Sue for wrongful dismissal damages', 
                 'merit_score': case.merit_score - 5, 'timeframe': '6-12 months'},
                {'name': 'Human Rights Tribunal', 'description': 'If discrimination involved', 
                 'merit_score': case.merit_score + 5 if 'discrimination' in case.description.lower() else 30, 
                 'timeframe': '8-18 months'}
            ]
        elif 'landlord' in case.legal_issue_type.lower() or 'tenant' in case.legal_issue_type.lower():
            legal_pathways = [
                {'name': 'LTB Application', 'description': 'File with Landlord Tenant Board', 
                 'merit_score': case.merit_score, 'timeframe': '2-4 months'},
                {'name': 'Negotiated Settlement', 'description': 'Direct negotiation with landlord/tenant', 
                 'merit_score': min(case.merit_score + 15, 100), 'timeframe': '1-4 weeks'}
            ]
        else:
            # Default pathways
            legal_pathways = [
                {'name': 'Court Application', 'description': 'File formal court application', 
                 'merit_score': case.merit_score, 'timeframe': '3-6 months'},
                {'name': 'Alternative Resolution', 'description': 'Explore settlement options', 
                 'merit_score': min(case.merit_score + 10, 100), 'timeframe': '1-3 months'}
            ]
    
    # Get available forms based on case type
    available_forms = get_available_forms(case)
    
    return render_template('cases/view.html', 
                         case=case, 
                         documents=documents,
                         legal_pathways=legal_pathways,
                         available_forms=available_forms)

@cases_bp.route('/')
@login_required
def list_cases():
    """List all user cases"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    cases = current_user.cases.order_by(Case.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('cases/list.html', cases=cases)

@cases_bp.route('/<int:case_id>/reanalyze', methods=['POST'])
@login_required
def reanalyze_case(case_id):
    """Re-run AI analysis on a case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    try:
        # Gather all text content
        full_text = case.description
        for doc in case.documents:
            if doc.extracted_text:
                full_text += f"\n\n{doc.extracted_text}"
        
        # Run AI analysis
        ai_analysis = analyze_legal_case(full_text, case.legal_issue_type)
        merit_score = calculate_merit_score(full_text, case.legal_issue_type, ai_analysis)
        
        # Update case
        case.classification = ai_analysis.get('classification', case.legal_issue_type)
        case.merit_score = merit_score
        case.ai_summary = ai_analysis.get('summary', '')
        case.recommended_actions = ai_analysis.get('recommendations', '')
        case.status = 'analyzed'
        case.analyzed_at = datetime.utcnow()
        
        db.session.commit()
        
        flash("Case analysis updated successfully!", 'success')
        
    except Exception as e:
        current_app.logger.error(f"Reanalysis failed: {e}")
        flash("Analysis update failed. Please try again later.", 'error')
    
    return redirect(url_for('cases.view_case', case_id=case_id))

@cases_bp.route('/<int:case_id>/delete', methods=['POST'])
@login_required
def delete_case(case_id):
    """Delete a case and associated documents"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    try:
        # Delete associated files
        for doc in case.documents:
            try:
                if os.path.exists(doc.file_path):
                    os.remove(doc.file_path)
            except Exception as e:
                current_app.logger.error(f"Failed to delete file {doc.file_path}: {e}")
        
        # Delete case (documents will be deleted via cascade)
        db.session.delete(case)
        db.session.commit()
        
        flash("Case deleted successfully", 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting case: {e}")
        flash("Failed to delete case. Please try again.", 'error')
    
    return redirect(url_for('cases.list_cases'))

@cases_bp.route('/<int:case_id>/add-evidence', methods=['GET', 'POST'])
@login_required
def add_evidence(case_id):
    """Add additional evidence to an existing case"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            uploaded_files = request.files.getlist('evidence_files[]')
            evidence_type = request.form.get('evidence_type', 'supporting')  # supporting, opposition, counter
            
            if not uploaded_files:
                flash('Please select at least one file to upload', 'warning')
                return redirect(url_for('cases.view_case', case_id=case_id))
            
            upload_folder = os.path.join(current_app.root_path, 'uploads', str(current_user.id))
            os.makedirs(upload_folder, exist_ok=True)
            
            added_count = 0
            for file in uploaded_files:
                if file and file.filename and allowed_file(file.filename):
                    # Generate unique filename
                    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'bin'
                    unique_filename = f"{uuid.uuid4()}.{file_ext}"
                    file_path = os.path.join(upload_folder, unique_filename)
                    
                    # Save file
                    file.save(file_path)
                    
                    # Extract text
                    try:
                        extracted_text = extract_text_from_file(file_path, file.content_type if file.content_type else 'application/octet-stream')
                    except:
                        extracted_text = ""
                    
                    # Create document record
                    doc = Document()
                    doc.case_id = case.id
                    doc.filename = secure_filename(file.filename)
                    doc.file_path = file_path
                    doc.file_type = file_ext
                    doc.extracted_text = extracted_text
                    doc.evidence_type = evidence_type
                    doc.uploaded_at = datetime.utcnow()
                    
                    db.session.add(doc)
                    added_count += 1
            
            if added_count > 0:
                # Re-analyze case with new evidence
                db.session.commit()
                
                # Trigger re-analysis
                full_text = case.description or ""
                for doc in case.documents:
                    if doc.extracted_text:
                        full_text += f"\n\n[{doc.evidence_type.upper()} EVIDENCE - {doc.filename}]:\n{doc.extracted_text}"
                
                # Run AI analysis with the new evidence
                ai_analysis = analyze_legal_case(full_text, case.legal_issue_type)
                merit_score = calculate_merit_score(full_text, case.legal_issue_type, ai_analysis)
                
                # Update case with new analysis
                case.merit_score = merit_score
                case.ai_analysis = json.dumps(ai_analysis) if ai_analysis else None
                case.ai_summary = ai_analysis.get('summary', '')
                case.recommended_actions = json.dumps(ai_analysis.get('recommendations', []))
                case.analyzed_at = datetime.utcnow()
                
                db.session.commit()
                flash(f'Successfully added {added_count} evidence file(s) and updated case analysis', 'success')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding evidence: {e}")
            flash('Error adding evidence. Please try again.', 'error')
    
    return redirect(url_for('cases.view_case', case_id=case_id))

@cases_bp.route('/<int:case_id>/generate-document')
@login_required
def generate_document_form(case_id):
    """Show document generation form"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    if not case.merit_score or case.merit_score < 40:
        flash("Your case needs further analysis before generating documents", 'warning')
        return redirect(url_for('cases.view_case', case_id=case_id))
    
    return render_template('cases/generate_document.html', case=case)

@cases_bp.route('/<int:case_id>/generate-document', methods=['POST'])
@login_required
def generate_document(case_id):
    """Generate court document with AI pre-filling and free user tracking"""
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    
    # Import needed modules
    from flask import make_response
    from models import User
    
    # Check merit score
    if not case.merit_score or case.merit_score < 40:
        flash("Your case needs a merit score of at least 40% to generate documents.", 'warning')
        return redirect(url_for('cases.view_case', case_id=case_id))
    
    # Check if user is in pilot program (first 1000 users)
    if not current_user.is_test_user:
        # Count non-test users
        real_user_count = User.query.filter_by(is_test_user=False).count()
        if real_user_count <= 1000:
            # User is part of free pilot program - mark them as test user
            current_user.is_test_user = True
            db.session.commit()
        else:
            # Check if user has document credits
            if not hasattr(current_user, 'document_credits') or not current_user.document_credits or current_user.document_credits <= 0:
                flash("You need document credits to generate court documents. Please purchase credits.", 'warning')
                return redirect(url_for('pricing'))
    
    document_type = request.form.get('document_type', 'application')
    
    try:
        # Initialize legal engine for Canadian law lookup
        from canadian_legal_engine import CanadianLegalEngine
        legal_engine = CanadianLegalEngine()
        
        # Get relevant laws based on case
        case_facts = [case.description or ""]
        for doc in case.documents:
            if doc.extracted_text:
                case_facts.append(doc.extracted_text[:1000])
        
        relevant_laws = legal_engine.get_relevant_laws(current_user, case.legal_issue_type, case_facts)
        
        # Prepare evidence summary
        evidence_summary = ""
        supporting_evidence = []
        opposition_evidence = []
        
        for doc in case.documents:
            if doc.evidence_type == 'supporting':
                supporting_evidence.append(f"- {doc.filename}: {doc.extracted_text[:200]}..." if doc.extracted_text else f"- {doc.filename}")
            elif doc.evidence_type == 'opposition':
                opposition_evidence.append(f"- {doc.filename}: {doc.extracted_text[:200]}..." if doc.extracted_text else f"- {doc.filename}")
        
        # Determine court based on case type and location
        court_name = "SUPERIOR COURT OF JUSTICE"
        if 'family' in case.legal_issue_type.lower():
            court_name = "FAMILY COURT"
        elif 'small_claims' in case.legal_issue_type.lower():
            court_name = "SMALL CLAIMS COURT"
        elif 'landlord' in case.legal_issue_type.lower() or 'tenant' in case.legal_issue_type.lower():
            court_name = "LANDLORD AND TENANT BOARD"
        
        # Generate court document with AI analysis and evidence
        document_content = f"""
{current_user.province.upper() if current_user.province else 'ONTARIO'}
{court_name}

COURT FILE NO: {case.id}-{datetime.now().strftime('%Y')}

BETWEEN:

{current_user.full_name.upper()}
                                                    Applicant/Plaintiff
- and -

[RESPONDENT NAME TO BE FILLED]
                                                    Respondent/Defendant

{document_type.upper().replace('_', ' ')}

TO THE HONOURABLE COURT:

1. CASE OVERVIEW
   Case Title: {case.title}
   Legal Issue Type: {case.legal_issue_type.replace('_', ' ').title()}
   Merit Score: {case.merit_score}% (AI-analyzed strength of case)
   Date Filed: {datetime.now().strftime('%B %d, %Y')}

2. APPLICANT INFORMATION
   Name: {current_user.full_name}
   Email: {current_user.email}
   City: {current_user.city}, {current_user.province}
   Postal Code: {current_user.postal_code or '[TO BE PROVIDED]'}

3. AI LEGAL ANALYSIS SUMMARY
{case.ai_summary or 'Comprehensive legal analysis indicates strong grounds for proceeding.'}

4. STATEMENT OF FACTS
{case.description}

5. EVIDENCE SUBMITTED
   
   A. SUPPORTING EVIDENCE (Applicant's Evidence):
{chr(10).join(supporting_evidence) if supporting_evidence else '   [No supporting evidence uploaded]'}
   
   B. OPPOSITION EVIDENCE (Respondent's Evidence):
{chr(10).join(opposition_evidence) if opposition_evidence else '   [No opposition evidence uploaded]'}

6. APPLICABLE LAW
   
   A. FEDERAL LAWS:
{chr(10).join([f"   - {law['act']}: Sections {', '.join(map(str, law['sections'][:5]))}" for law in relevant_laws.get('federal_laws', [])[:3]])}
   
   B. PROVINCIAL LAWS ({current_user.province.upper() if current_user.province else 'ONTARIO'}):
{chr(10).join([f"   - {law['act']}: {law.get('description', '')}" for law in relevant_laws.get('provincial_laws', [])[:3]])}
   
   C. CHARTER RIGHTS:
{chr(10).join([f"   - {right}" for right in relevant_laws.get('charter_rights', [])[:3]])}

7. RELIEF SOUGHT
   The Applicant respectfully requests that this Honourable Court:
   
   a) Grant the relief as set out in the attached Schedule A;
   b) Award costs of this application;
   c) Grant such further and other relief as this Honourable Court deems just.

8. GROUNDS FOR APPLICATION
   This application is made on the following grounds:
   {chr(10).join([f"   {i+1}. {action}" for i, action in enumerate(json.loads(case.recommended_actions) if case.recommended_actions else [])])}

9. EVIDENCE TO BE RELIED UPON
   - All documents uploaded and analyzed by AI
   - Affidavit of {current_user.full_name} to be sworn
   - Such further evidence as counsel may advise

10. APPLICABLE RULES
    This application is made under Rules 14, 16, and 38 of the Rules of Civil Procedure.

ALL OF WHICH IS RESPECTFULLY SUBMITTED this {datetime.now().strftime('%d')}th day of {datetime.now().strftime('%B, %Y')}.

_________________________________
{current_user.full_name}
Applicant (Self-Represented)

FILING INSTRUCTIONS:
1. Complete any sections marked [TO BE FILLED]
2. Review all information for accuracy
3. File at: {court_name}, {current_user.city}, {current_user.province}
4. Serve on all parties within required timelines
5. Filing Fee: ${relevant_laws.get('filing_fee', 'Check with court')}

IMPORTANT NOTICE:
This document was generated by SmartDispute.ai based on AI analysis of your evidence and applicable Canadian law. 
While comprehensive, you should review this document carefully and consider consulting with a lawyer before filing.
SmartDispute.ai provides legal information, not legal advice.

---
DOCUMENT GENERATED BY SMARTDISPUTE.AI
Document ID: SD-{datetime.now().strftime('%Y%m%d')}-{case.id}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Merit Score: {case.merit_score}%
User Status: {'FREE PILOT USER' if current_user.is_test_user else 'PAID USER'}
"""
        
        # Store generated document status
        case.document_generated = True
        case.status = 'document_generated'
        
        # Deduct credit if not a pilot user
        if not current_user.is_test_user and hasattr(current_user, 'document_credits') and current_user.document_credits:
            current_user.document_credits -= 1
        
        db.session.commit()
        
        # Create downloadable file
        filename = f"SmartDispute_{document_type}_{case.id}_{datetime.now().strftime('%Y%m%d')}.txt"
        
        response = make_response(document_content)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        flash("Court document generated successfully! Review it carefully before filing.", 'success')
        return response
        
    except Exception as e:
        current_app.logger.error(f"Document generation failed: {e}")
        flash("Document generation failed. Please try again.", 'error')
        return redirect(url_for('cases.view_case', case_id=case_id))