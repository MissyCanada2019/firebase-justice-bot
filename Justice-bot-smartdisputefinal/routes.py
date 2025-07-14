import os
import uuid
import logging
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import (
    render_template, request, redirect, url_for, flash, 
    session, jsonify, send_file, abort
)
from flask_login import login_user, logout_user, login_required, current_user

from sqlalchemy import func
from database import db
from models import User, Case, Document, Payment, ChatSession, ChatMessage, CaseMeritScore, Testimonial, GeneratedForm, MailingRequest
from utils.ocr import process_document
from utils.legal_analyzer import analyze_case, get_merit_score, get_recommended_forms
from utils.document_generator import generate_legal_document
from utils.canlii_api import search_canlii, get_relevant_precedents
# Using our new payment_service module
# from utils.payment import process_paypal_payment
from utils.ai_chat import generate_ai_response
from utils.mailing_service import calculate_mailing_cost, validate_mailing_address, create_mailing_request, get_mailing_request_status, get_available_mailing_options, queue_mailing_request

# Function to register all routes with the Flask app
def register_routes(app):
    """
    Register all routes with the Flask app
    This function is called from main.py
    """
    # Check if routes are already registered
    if hasattr(app, '_routes_registered') and app._routes_registered:
        app.logger.info("Routes already registered, skipping")
        return app
        
    app.logger.info("Registering main application routes")
    init_routes(app)
    
    # Mark routes as registered
    app._routes_registered = True
    return app

def init_routes(app):
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
    
    @app.route('/google4b945706e36a5db4.html')
    def google_verification():
        return 'google-site-verification: google4b945706e36a5db4.html'
        
    @app.route('/google9fGsDdnUDR_1_WC3hApOV0nkhDs7MQL9ZVA1s5UC5nU.html')
    def google_verification_new():
        return 'google-site-verification: google9fGsDdnUDR_1_WC3hApOV0nkhDs7MQL9ZVA1s5UC5nU.html'
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @app.route('/')
    def index():
        # Get featured testimonials for homepage
        featured_testimonials = Testimonial.query.filter_by(is_featured=True, is_approved=True).order_by(Testimonial.created_at.desc()).limit(3).all()
        return render_template('index.html', testimonials=featured_testimonials)
        
    @app.route('/about')
    def about():
        # Get all approved testimonials for the about page
        testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
        return render_template('about.html', testimonials=testimonials)
        
    @app.route('/founders-story')
    def founders_story():
        """Founder's personal story page"""
        return render_template('founders_story.html')
        
    @app.route('/testimonials')
    def testimonials():
        # Get all approved testimonials
        testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
        return render_template('testimonials.html', testimonials=testimonials)
        
    @app.route('/add-testimonial', methods=['GET', 'POST'])
    @login_required
    def add_testimonial():
        if request.method == 'POST':
            name = request.form.get('name')
            role = request.form.get('role')
            location = request.form.get('location')
            content = request.form.get('content')
            rating = request.form.get('rating')
            case_type = request.form.get('case_type')
            
            if not name or not content:
                flash('Name and testimonial content are required', 'danger')
                return redirect(url_for('add_testimonial'))
                
            # Create new testimonial, pending approval
            new_testimonial = Testimonial(
                name=name,
                role=role,
                location=location,
                content=content,
                rating=int(rating) if rating else None,
                case_type=case_type,
                is_approved=False  # Requires admin approval
            )
            
            db.session.add(new_testimonial)
            db.session.commit()
            
            flash('Thank you for your testimonial! It will be reviewed before publishing.', 'success')
            return redirect(url_for('testimonials'))
            
        return render_template('add_testimonial.html')
        
    @app.route('/admin/testimonials')
    @login_required
    def admin_testimonials():
        # Only allow admins
        if current_user.role != 'admin':
            abort(403)
            
        # Get all testimonials, including unapproved ones
        testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
        return render_template('admin/testimonials.html', testimonials=testimonials)
        
    @app.route('/admin/testimonials/<int:testimonial_id>/approve', methods=['POST'])
    @login_required
    def approve_testimonial(testimonial_id):
        # Only allow admins
        if current_user.role != 'admin':
            abort(403)
            
        testimonial = Testimonial.query.get_or_404(testimonial_id)
        testimonial.is_approved = True
        db.session.commit()
        
        flash('Testimonial approved and now visible', 'success')
        return redirect(url_for('admin_testimonials'))
        
    @app.route('/admin/testimonials/<int:testimonial_id>/feature', methods=['POST'])
    @login_required
    def feature_testimonial(testimonial_id):
        # Only allow admins
        if current_user.role != 'admin':
            abort(403)
            
        testimonial = Testimonial.query.get_or_404(testimonial_id)
        testimonial.is_featured = not testimonial.is_featured  # Toggle the feature status
        db.session.commit()
        
        if testimonial.is_featured:
            flash('Testimonial is now featured on the homepage', 'success')
        else:
            flash('Testimonial is no longer featured', 'info')
        return redirect(url_for('admin_testimonials'))
        
    @app.route('/admin/testimonials/<int:testimonial_id>/delete', methods=['POST'])
    @login_required
    def delete_testimonial(testimonial_id):
        # Only allow admins
        if current_user.role != 'admin':
            abort(403)
            
        testimonial = Testimonial.query.get_or_404(testimonial_id)
        db.session.delete(testimonial)
        db.session.commit()
        
        flash('Testimonial deleted', 'success')
        return redirect(url_for('admin_testimonials'))
        
    @app.route('/legal-disclaimer')
    def legal_disclaimer():
        return render_template('legal_disclaimer.html')
        
    @app.route('/privacy-policy')
    def privacy_policy():
        return render_template('privacy_policy.html')
        
    @app.route('/terms-of-service')
    def terms_of_service():
        return render_template('terms_of_service.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        try:
            app.logger.debug("Login route accessed")
            # Count registered users for debugging (avoid fetching all columns)
            try:
                user_count = db.session.query(func.count(User.id)).scalar()
                app.logger.debug(f"DB contains {user_count} users")
            except Exception as count_err:
                app.logger.warning(f"Error counting users: {str(count_err)}")
                user_count = "unknown"
                
            app.logger.debug(f"DB contains {user_count} users")

            if current_user.is_authenticated:
                app.logger.debug(f"User already authenticated as: {current_user.email}")
                return redirect(url_for('dashboard'))
                
            if request.method == 'POST':
                email = request.form.get('email')
                password = request.form.get('password')
                
                app.logger.info(f"Login attempt for email: {email}")
                app.logger.debug(f"Form data: {request.form}")
                
                try:
                    # Explicitly test database connection
                    user = User.query.filter_by(email=email).first()
                    app.logger.debug(f"Database query completed successfully")
                except Exception as db_err:
                    app.logger.error(f"Database error during user lookup: {str(db_err)}", exc_info=True)
                    flash('Unable to connect to the database. Please try again later.', 'danger')
                    return render_template('login.html', debug_msg="DB connection error")
                
                if not user:
                    app.logger.warning(f"No user found with email: {email}")
                    flash('Invalid email or password', 'danger')
                    return render_template('login.html', debug_msg="User not found")
                
                app.logger.debug(f"Found user: {user.id} with email: {user.email}")
                app.logger.debug(f"Password hash: {user.password_hash[:10]}... (length={len(user.password_hash) if user.password_hash else 0})")
                
                try:
                    password_correct = user.check_password(password)
                    app.logger.debug(f"Password check result: {password_correct}")
                except Exception as pwd_err:
                    app.logger.error(f"Error checking password: {str(pwd_err)}", exc_info=True)
                    flash('Error validating credentials. Please try again.', 'danger')
                    return render_template('login.html', debug_msg="Password check error")
                
                if password_correct:
                    app.logger.info(f"Successful password check for user: {email}")
                    
                    try:
                        login_user(user)
                        app.logger.debug(f"User logged in successfully with id: {user.id}")
                        
                        # Update last login timestamp if the column exists
                        try:
                            user.last_login = datetime.utcnow()
                            db.session.commit()
                            app.logger.debug("Last login timestamp updated")
                        except Exception as ts_err:
                            app.logger.warning(f"Could not update last_login timestamp: {str(ts_err)}")
                            # Roll back the failed timestamp update but keep the user logged in
                            db.session.rollback()
                        
                        next_page = request.args.get('next')
                        return redirect(next_page or url_for('dashboard'))
                    except Exception as login_err:
                        app.logger.error(f"Error during login_user: {str(login_err)}", exc_info=True)
                        flash('Error during login process. Please try again.', 'danger')
                        return render_template('login.html', debug_msg="Login user error")
                else:
                    app.logger.warning(f"Invalid password for user: {email}")
                    flash('Invalid email or password', 'danger')
                    return render_template('login.html', debug_msg="Invalid password")
                    
            return render_template('login.html')
        except Exception as e:
            app.logger.error(f"Unhandled error in login route: {str(e)}", exc_info=True)
            flash('An error occurred while processing your request. Please try again later.', 'danger')
            return render_template('login.html', debug_msg=f"Exception: {str(e)}")

    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        # Get current user count for display (excluding test users from the limit)
        real_user_count = User.query.filter_by(is_free_user=True, is_test_user=False).count()
        
        if request.method == 'POST':
            # Check if we've reached the 1000 real user limit
            if real_user_count >= 1000:
                flash('The free pilot program is now full. We have reached our limit of 1000 participants. Thank you for your interest!', 'warning')
                return render_template('register.html', user_count=real_user_count, program_full=True)
            
            # Get form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            city = request.form.get('city')
            province = request.form.get('province')
            postal_code = request.form.get('postal_code')
            legal_issue_type = request.form.get('legal_issue_type')
            password = request.form.get('password')
            password_confirm = request.form.get('password_confirm')
            pilot_consent = request.form.get('pilot_consent') == 'on'
            
            # Validation
            if not all([first_name, last_name, email, phone, address, city, province, postal_code, legal_issue_type, password]):
                flash('All fields are required', 'danger')
                return render_template('register.html', user_count=real_user_count)
            
            if password != password_confirm:
                flash('Passwords do not match', 'danger')
                return render_template('register.html', user_count=real_user_count)
                
            if not pilot_consent:
                flash('You must agree to participate in the pilot program to continue', 'danger')
                return render_template('register.html', user_count=real_user_count)
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already exists', 'danger')
                return render_template('register.html', user_count=real_user_count)
                
            # Create new comprehensive user profile
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                province=province,
                postal_code=postal_code,
                legal_issue_type=legal_issue_type,
                is_free_user=True,
                is_test_user=False,  # Real users are not test users
                free_user_number=real_user_count + 1,
                pilot_consent=True,
                email_verified=True
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'Welcome to SmartDispute.ai! You are participant #{new_user.free_user_number}/1000 in our free pilot program. Your account is ready for legal case management.', 'success')
            return redirect(url_for('login'))
            
        return render_template('register.html', user_count=real_user_count)
    
    @app.route('/logout')
    @login_required
    def logout():
        # We use a standard Flask-Login logout
        logout_user()
        flash("You have been successfully logged out", "success")
        return redirect(url_for('index'))
        
    @app.route('/profile')
    @login_required
    def profile():
        # Count user's data
        case_count = Case.query.filter_by(user_id=current_user.id).count()
        document_count = Document.query.filter_by(user_id=current_user.id).count()
        form_count = GeneratedForm.query.filter_by(user_id=current_user.id).count()
        mailing_count = MailingRequest.query.filter_by(user_id=current_user.id).count()
        
        # Get recent payments
        payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).limit(5).all()
        
        return render_template('profile.html', 
                               case_count=case_count, 
                               document_count=document_count, 
                               form_count=form_count,
                               mailing_count=mailing_count,
                               payments=payments,
                               now=datetime.utcnow())
    
    @app.route('/update_profile', methods=['POST'])
    @login_required
    def update_profile():
        email = request.form.get('email')
        username = request.form.get('username')
        
        if not email or not username:
            flash('Email and username are required', 'danger')
            return redirect(url_for('profile'))
        
        # Check if username or email already exists (excluding current user)
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email),
            User.id != current_user.id
        ).first()
        
        if existing_user:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('profile'))
        
        # Update user
        current_user.email = email
        current_user.username = username
        db.session.commit()
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    @app.route('/change_password', methods=['POST'])
    @login_required
    def change_password():
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required', 'danger')
            return redirect(url_for('profile'))
        
        # Check if current password is correct
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('profile'))
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('profile'))
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('profile'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        user_cases = Case.query.filter_by(user_id=current_user.id).order_by(Case.updated_at.desc()).all()
        return render_template('dashboard.html', cases=user_cases)
    
    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload():
        if request.method == 'POST':
            # Check if case title exists
            case_title = request.form.get('case_title')
            case_type = request.form.get('case_category')
            
            if not case_title or not case_type:
                flash('Please provide a case title and select a category', 'danger')
                return redirect(url_for('upload'))
                
            # Create a new case
            new_case = Case(
                user_id=current_user.id,
                title=case_title,
                case_type=case_type
            )
            db.session.add(new_case)
            db.session.commit()
            
            # Check if files were uploaded
            if 'files[]' not in request.files:
                flash('No files selected', 'danger')
                return redirect(url_for('upload'))
                
            files = request.files.getlist('files[]')
            
            # Create user directory if it doesn't exist
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Process each file
            files_processed = 0
            for file in files:
                if file and allowed_file(file.filename):
                    try:
                        # Get file information
                        original_filename = secure_filename(file.filename)
                        if '.' in original_filename:
                            file_extension = original_filename.rsplit('.', 1)[1].lower()
                        else:
                            file_extension = 'unknown'
                            
                        # Create unique filename
                        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                        
                        # Log upload attempt
                        app.logger.info(f"Saving file: {original_filename} (size: {file.content_length if hasattr(file, 'content_length') else 'unknown'})")
                        
                        # Save file to disk
                        file_path = os.path.join(user_dir, unique_filename)
                        file.save(file_path)
                        app.logger.info(f"File saved successfully to {file_path}")
                        
                        # Process document with OCR - with error handling
                        try:
                            extracted_text, metadata = process_document(file_path, file_extension)
                        except Exception as e:
                            app.logger.error(f"Error processing document: {str(e)}")
                            extracted_text = "Error extracting text. The file may be corrupted or in an unsupported format."
                            metadata = {"error": str(e)}
                        
                        # Save document info to database
                        new_document = Document(
                            user_id=current_user.id,
                            case_id=new_case.id,
                            filename=original_filename,
                            file_path=file_path,
                            file_type=file_extension,
                            extracted_text=extracted_text,
                            doc_metadata=metadata
                        )
                        db.session.add(new_document)
                        files_processed += 1
                    except Exception as e:
                        app.logger.error(f"Error handling file upload: {str(e)}")
                        flash(f"Error uploading {file.filename}: {str(e)}", 'danger')
            
            db.session.commit()
            
            if files_processed > 0:
                flash(f"Successfully uploaded {files_processed} files", 'success')
                return redirect(url_for('analyze', case_id=new_case.id))
            else:
                flash("No files were successfully uploaded. Please try again with supported file types.", 'warning')
                return redirect(url_for('upload'))
            
        return render_template('upload.html')
    
    @app.route('/add_files/<int:case_id>', methods=['GET', 'POST'])
    @login_required
    def add_files(case_id):
        """Route for adding more files to an existing case"""
        # Get case
        case = Case.query.get_or_404(case_id)
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            abort(403)
            
        if request.method == 'POST':
            # Check if files were uploaded
            if 'files[]' not in request.files:
                flash('No files selected', 'danger')
                return redirect(url_for('add_files', case_id=case_id))
                
            files = request.files.getlist('files[]')
            
            # Create user directory if it doesn't exist
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Process each file
            files_processed = 0
            for file in files:
                if file and allowed_file(file.filename):
                    try:
                        # Get file information
                        original_filename = secure_filename(file.filename)
                        if '.' in original_filename:
                            file_extension = original_filename.rsplit('.', 1)[1].lower()
                        else:
                            file_extension = 'unknown'
                            
                        # Create unique filename
                        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                        
                        # Log upload attempt
                        app.logger.info(f"Saving file: {original_filename} (size: {file.content_length if hasattr(file, 'content_length') else 'unknown'})")
                        
                        # Save file to disk
                        file_path = os.path.join(user_dir, unique_filename)
                        file.save(file_path)
                        app.logger.info(f"File saved successfully to {file_path}")
                        
                        # Process document with OCR - with error handling
                        try:
                            extracted_text, metadata = process_document(file_path, file_extension)
                        except Exception as e:
                            app.logger.error(f"Error processing document: {str(e)}")
                            extracted_text = "Error extracting text. The file may be corrupted or in an unsupported format."
                            metadata = {"error": str(e)}
                        
                        # Save document info to database
                        new_document = Document(
                            user_id=current_user.id,
                            case_id=case.id,
                            filename=original_filename,
                            file_path=file_path,
                            file_type=file_extension,
                            extracted_text=extracted_text,
                            doc_metadata=metadata
                        )
                        db.session.add(new_document)
                        files_processed += 1
                    except Exception as e:
                        app.logger.error(f"Error handling file upload: {str(e)}")
                        flash(f"Error uploading {file.filename}: {str(e)}", 'danger')
            
            db.session.commit()
            
            if files_processed > 0:
                flash(f"Successfully added {files_processed} new documents to your case", 'success')
                # Update the case modified time
                case.updated_at = datetime.utcnow()
                db.session.commit()
                return redirect(url_for('analyze', case_id=case.id))
            else:
                flash("No files were successfully uploaded. Please try again with supported file types.", 'warning')
                return redirect(url_for('add_files', case_id=case_id))
        
        # GET request - show form
        return render_template('add_files.html', case=case)
    
    @app.route('/analyze/<int:case_id>')
    @login_required
    def analyze(case_id):
        try:
            case = Case.query.get_or_404(case_id)
            
            # Check if user owns the case
            if case.user_id != current_user.id:
                abort(403)
                
            # Get documents for this case
            documents = Document.query.filter_by(case_id=case.id).all()
            
            # If no documents, redirect to upload
            if not documents:
                flash('Please upload documents first', 'warning')
                return redirect(url_for('upload'))
            
            # Add debug log    
            logging.debug(f"Starting analysis for case {case_id} with {len(documents)} documents")
            
            # Analyze case with robust error handling
            try:
                analysis = analyze_case(case, documents)
                logging.debug(f"Analysis successful for case {case_id}")
                
                # Check if analysis failed due to OpenAI API quota or rate limit issues
                if 'error' in analysis and ('quota' in analysis['error'].lower() or '429' in analysis['error']):
                    flash('Advanced AI analysis is temporarily unavailable due to high demand. We\'re using our standard analysis instead.', 'warning')
                
            except Exception as e:
                error_msg = str(e)
                logging.error(f"Error in analyze_case: {error_msg}")
                
                # Check for OpenAI quota errors specifically to show user-friendly message
                if 'quota' in error_msg.lower() or '429' in error_msg or 'rate limit' in error_msg.lower():
                    flash('Advanced AI analysis is temporarily unavailable due to high demand. We\'re using our standard analysis instead.', 'warning')
                else:
                    flash('An error occurred during analysis. Using basic analysis instead.', 'warning')
                
                # Provide a fallback analysis structure if the full analysis fails
                analysis = {
                    'case_id': case.id,
                    'category_scores': {'fallback': 0},
                    'detected_issues': [],
                    'key_entities': {},
                    'dates': [],
                    'names': [],
                    'analysis_method': 'error',
                    'error': error_msg
                }
                flash('We encountered an issue analyzing your documents. Some features may be limited.', 'warning')
            
            # Update case with merit score with error handling
            try:
                merit_score = get_merit_score(analysis)
                case.merit_score = merit_score
                db.session.commit()
                logging.debug(f"Merit score calculated: {merit_score}")
            except Exception as e:
                logging.error(f"Error calculating merit score: {str(e)}")
                merit_score = 0.5  # Default middle score
                flash('We encountered an issue calculating your case score.', 'warning')
            
            # Get enhanced relevant precedents with robust error handling
            try:
                precedents = get_relevant_precedents(case.case_type, analysis)
                logging.debug(f"Precedents retrieved for category {case.case_type}")
            except Exception as e:
                logging.error(f"Error retrieving precedents: {str(e)}")
                precedents = {
                    'landmark_cases': [],
                    'recent_cases': [],
                    'related_cases': [],
                    'metadata': {'category': case.case_type, 'search_date': datetime.now().strftime('%Y-%m-%d')}
                }
            
            # Get recommended forms with error handling
            try:
                recommended_forms = get_recommended_forms(case.case_type, analysis)
                logging.debug(f"Retrieved {len(recommended_forms)} recommended forms")
            except Exception as e:
                logging.error(f"Error getting recommended forms: {str(e)}")
                recommended_forms = []
            
            # Log precedent search info
            if precedents and 'metadata' in precedents:
                logging.info(f"Found precedents in {precedents['metadata'].get('category')} with {len(precedents.get('top_precedents', []))} top results")
            
            return render_template(
                'analyze.html', 
                case=case, 
                documents=documents, 
                analysis=analysis,
                merit_score=merit_score,
                precedents=precedents,
                recommended_forms=recommended_forms
            )
        except Exception as e:
            logging.error(f"Unhandled error in analyze route: {str(e)}")
            flash('An unexpected error occurred. Please try again later.', 'danger')
            return redirect(url_for('dashboard'))
        
    
    @app.route('/generate/<int:case_id>', methods=['GET', 'POST'])
    @login_required
    def generate(case_id):
        case = Case.query.get_or_404(case_id)
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            abort(403)
            
        if request.method == 'POST':
            form_type = request.form.get('form_type')
            if not form_type:
                flash('Please select a form type', 'danger')
                return redirect(url_for('generate', case_id=case.id))
                
            # Get form data from request
            form_data = {}
            for key, value in request.form.items():
                if key != 'form_type' and key != 'csrf_token':
                    form_data[key] = value
                    
            # Check for selected documents
            selected_doc_ids = request.form.getlist('doc_ids') or []
            
            # Generate legal document
            try:
                if selected_doc_ids:
                    # If specific documents were selected, use only those
                    documents = Document.query.filter(
                        Document.case_id == case.id, 
                        Document.id.in_(selected_doc_ids)
                    ).all()
                else:
                    # Otherwise use all documents
                    documents = Document.query.filter_by(case_id=case.id).all()
                
                file_path, citations = generate_legal_document(
                    case, 
                    documents, 
                    form_type, 
                    form_data
                )
                
                # Save generated form
                new_form = GeneratedForm(
                    case_id=case.id,
                    form_type=form_type,
                    form_data=form_data,
                    generated_file_path=file_path,
                    citations=citations
                )
                db.session.add(new_form)
                db.session.commit()
                
                return redirect(url_for('preview', form_id=new_form.id))
                
            except Exception as e:
                logging.error(f"Error generating document: {str(e)}")
                flash('Error generating document. Please try again.', 'danger')
                return redirect(url_for('generate', case_id=case.id))
        
        # Handle GET request with pre-selected documents and form
        selected_doc_ids = request.args.getlist('doc_ids')
        selected_form_id = request.args.get('form_id')
        
        # Get recommended forms for this case with error handling
        try:
            if selected_doc_ids:
                # If specific documents were selected from analyze page
                documents = Document.query.filter(
                    Document.case_id == case.id, 
                    Document.id.in_(selected_doc_ids)
                ).all()
                
                if not documents:
                    # Fallback to all documents if none found with selected IDs
                    documents = Document.query.filter_by(case_id=case.id).all()
            else:
                # Use all documents
                documents = Document.query.filter_by(case_id=case.id).all()
                
            analysis = analyze_case(case, documents)
            recommended_forms = get_recommended_forms(case.case_type, analysis)
            
            # If a specific form ID was selected in analyze page,
            # pre-select it on generate page
            if selected_form_id:
                for form in recommended_forms:
                    if form.get('id') == selected_form_id:
                        form['selected'] = True
                        break
                        
        except Exception as e:
            logging.error(f"Error getting recommended forms in generate route: {str(e)}")
            flash('We encountered an issue loading recommended forms.', 'warning')
            recommended_forms = []
        
        return render_template('generate.html', case=case, recommended_forms=recommended_forms)
    
    @app.route('/preview/<int:form_id>')
    @login_required
    def preview(form_id):
        form = GeneratedForm.query.get_or_404(form_id)
        case = Case.query.get_or_404(form.case_id)
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            abort(403)
            
        # Check if subscription allows downloading without watermark
        can_download_clean = current_user.subscription_type != "free"
        
        return render_template('preview.html', form=form, case=case, can_download_clean=can_download_clean)
    
    @app.route('/download/<int:form_id>/<string:version>')
    @login_required
    def download(form_id, version):
        form = GeneratedForm.query.get_or_404(form_id)
        case = Case.query.get_or_404(form.case_id)
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            abort(403)
            
        # Check if user has permission to download clean version
        if version == 'clean' and current_user.subscription_type == 'free':
            flash('Please upgrade your subscription to download clean documents', 'warning')
            return redirect(url_for('pricing'))
            
        # If pay-per-document, check if paid
        if version == 'clean' and current_user.subscription_type == 'pay_per_doc' and not form.is_paid:
            return redirect(url_for('pay_document', form_id=form.id))
            
        # Get the file path based on version
        file_path = form.generated_file_path
        
        # For clean version, remove watermark if needed
        if version == 'clean' and not os.path.exists(file_path.replace('.pdf', '_clean.pdf')):
            # Logic to remove watermark would go here
            pass
            
        return send_file(file_path, as_attachment=True)
    
    @app.route('/pay_document/<int:form_id>', methods=['GET', 'POST'])
    @login_required
    def pay_document(form_id):
        form = GeneratedForm.query.get_or_404(form_id)
        case = Case.query.get_or_404(form.case_id)
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            abort(403)
        
        # Import payment services
        from utils.payment_service import create_paypal_order, process_paypal_payment
        from utils.stripe_service import STRIPE_PUBLISHABLE_KEY
            
        # The document fee is always $5.99 CAD
        document_fee = 5.99
        
        # Create a payment order if this is a GET request (initial page load)
        paypal_order = None
        if request.method == 'GET':
            # Check if we have PayPal credentials
            if os.environ.get('PAYPAL_CLIENT_ID') and os.environ.get('PAYPAL_CLIENT_SECRET'):
                # Create a PayPal order for this document
                paypal_order = create_paypal_order(
                    amount=document_fee,
                    description=f"SmartDispute.ai - Document: {form.form_type}"
                )
                
                if not paypal_order:
                    flash('Error creating payment. Please try again later.', 'danger')
            else:
                app.logger.warning("PayPal credentials not set in environment variables")
        
        # Process payment if this is a POST request
        if request.method == 'POST':
            payment_method = request.form.get('payment_method')
            
            if payment_method == 'paypal':
                paypal_order_id = request.form.get('paypal_order_id')
                
                if paypal_order_id:
                    # Process PayPal payment
                    payment_status = process_paypal_payment(paypal_order_id, document_fee)
                    
                    if payment_status == 'completed':
                        # Mark document as paid
                        form.is_paid = True
                        
                        # Record payment
                        payment = Payment(
                            user_id=current_user.id,
                            amount=document_fee,
                            payment_type='per_document',
                            payment_method='paypal',
                            payment_id=paypal_order_id,
                            status='completed',
                            generated_form_id=form.id,
                            service_details={
                                'form_type': form.form_type,
                                'payment_date': datetime.utcnow().isoformat()
                            }
                        )
                        db.session.add(payment)
                        db.session.commit()
                        
                        flash('Payment successful! You can now download the document.', 'success')
                        return redirect(url_for('preview', form_id=form.id))
                    else:
                        flash(f'Payment {payment_status}. Please try again.', 'danger')
            
            elif payment_method == 'stripe':
                # Stripe payments are handled via the redirect to Stripe Checkout
                # and then back to our success/cancel endpoints
                flash('Please complete the Stripe checkout process to finalize your payment.', 'info')
                return redirect(url_for('pay_document', form_id=form.id))
            
            else:
                flash('Invalid payment method selected.', 'danger')
                        
        return render_template('pay_document.html', form=form, case=case, 
                              document_fee=document_fee, paypal_order=paypal_order,
                              stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)
    
    @app.route('/create-stripe-session/<int:form_id>', methods=['GET'])
    @login_required
    def create_stripe_session(form_id):
        """Route to create a Stripe checkout session for a document payment"""
        form = GeneratedForm.query.get_or_404(form_id)
        case = Case.query.get_or_404(form.case_id)
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Import stripe service
        from utils.stripe_service import create_checkout_session
        
        # The document fee is always $5.99 CAD
        document_fee = 5.99
        
        # Create a Stripe checkout session
        session = create_checkout_session(
            amount=document_fee,
            description=f"SmartDispute.ai - Document: {form.form_type}",
            payment_type='document',
            metadata={
                'form_id': form.id,
                'case_id': case.id,
                'user_id': current_user.id,
                'form_type': form.form_type
            }
        )
        
        if not session:
            return jsonify({'error': 'Could not create checkout session. Please try again later.'}), 500
        
        return jsonify(session)
    
    @app.route('/payment/success', methods=['GET'])
    @login_required
    def payment_success():
        """Route for successful Stripe payment callback"""
        session_id = request.args.get('session_id')
        
        if not session_id:
            flash('No payment information received.', 'warning')
            return redirect(url_for('dashboard'))
        
        # Import stripe service
        from utils.stripe_service import retrieve_session, verify_payment
        
        # Verify the payment
        session = retrieve_session(session_id)
        
        if not session:
            flash('Could not verify payment. Please contact support.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get metadata from session
        metadata = session.metadata
        payment_type = metadata.get('payment_type', 'unknown')
        
        if payment_type == 'document':
            try:
                form_id = int(metadata.get('form_id'))
                form = GeneratedForm.query.get_or_404(form_id)
                
                # Verify the payment status
                payment_status = verify_payment(session_id)
                
                if payment_status == 'completed':
                    # Mark document as paid
                    form.is_paid = True
                    
                    # Record payment
                    payment = Payment(
                        user_id=current_user.id,
                        amount=session.amount_total / 100.0,  # Convert from cents to dollars
                        payment_type='per_document',
                        payment_method='stripe',
                        payment_id=session.id,
                        status='completed',
                        generated_form_id=form.id,
                        service_details={
                            'form_type': form.form_type,
                            'case_id': int(metadata.get('case_id')),
                            'payment_date': datetime.utcnow().isoformat()
                        }
                    )
                    db.session.add(payment)
                    db.session.commit()
                    
                    flash('Payment completed successfully! You can now download your document.', 'success')
                    return redirect(url_for('preview', form_id=form.id))
                else:
                    flash(f'Payment {payment_status}. Please try again.', 'danger')
                    return redirect(url_for('pay_document', form_id=form.id))
            except (ValueError, KeyError, TypeError) as e:
                app.logger.error(f"Error processing Stripe payment: {str(e)}")
                flash('Error processing payment. Please contact support.', 'danger')
                return redirect(url_for('dashboard'))
        
        elif payment_type == 'subscription':
            # Process subscription payment similar to document payment
            flash('Subscription payment completed! Your account has been upgraded.', 'success')
            return redirect(url_for('dashboard'))
        
        else:
            flash('Unknown payment type. Please contact support.', 'warning')
            return redirect(url_for('dashboard'))
    
    @app.route('/payment/cancel', methods=['GET'])
    @login_required
    def payment_cancel():
        """Route for cancelled Stripe payment"""
        flash('Payment cancelled. You can try again when you\'re ready.', 'info')
        return redirect(url_for('dashboard'))
    
    @app.route('/pricing', methods=['GET'])
    def pricing():
        return render_template('pricing.html')
        
    @app.route('/subscription', methods=['GET'])
    @login_required
    def subscription():
        paypal_client_id = os.environ.get('PAYPAL_CLIENT_ID', '')
        if not paypal_client_id:
            flash('Payment processing is currently unavailable. Please try again later.', 'warning')
            return redirect(url_for('pricing'))
            
        return render_template('subscription.html', paypal_client_id=paypal_client_id)
        
    @app.route('/subscribe', methods=['POST'])
    @login_required
    def subscribe():
        # Import payment service
        from utils.payment_service import process_paypal_payment
        
        plan_type = request.form.get('plan_type')
        paypal_order_id = request.form.get('paypal_order_id')
        
        # Set subscription details based on plan type
        if plan_type == 'monthly':
            amount = 49.99
            subscription_end = datetime.utcnow() + timedelta(days=30)
        elif plan_type == 'annual':
            amount = 699.99
            subscription_end = datetime.utcnow() + timedelta(days=365)
        elif plan_type == 'low_income':
            amount = 25.00
            subscription_end = datetime.utcnow() + timedelta(days=365)
        else:
            flash('Invalid subscription plan selected.', 'danger')
            return redirect(url_for('pricing'))
        
        # Process the payment
        if paypal_order_id:
            payment_status = process_paypal_payment(paypal_order_id, amount)
            
            if payment_status == 'completed':
                # Update user subscription
                current_user.subscription_type = plan_type
                current_user.subscription_end = subscription_end
                
                # Record payment
                payment = Payment(
                    user_id=current_user.id,
                    amount=amount,
                    payment_type='subscription',
                    payment_method='paypal',
                    payment_id=paypal_order_id,
                    status='completed',
                    service_details={
                        'plan_type': plan_type,
                        'payment_date': datetime.utcnow().isoformat(),
                        'subscription_end': subscription_end.isoformat()
                    }
                )
                db.session.add(payment)
                db.session.commit()
                
                flash(f'Subscription to {plan_type} plan successful! Your subscription is active until {subscription_end.strftime("%Y-%m-%d")}.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash(f'Payment {payment_status}. Please try again.', 'danger')
        else:
            flash('No payment information received. Please try again.', 'danger')
            
        return redirect(url_for('pricing'))
    
    @app.route('/chat', methods=['GET', 'POST'])
    @login_required
    def chat():
        # Get or create a chat session
        case_id = request.args.get('case_id')
        
        if case_id:
            case = Case.query.get_or_404(int(case_id))
            # Check if user owns the case
            if case.user_id != current_user.id:
                abort(403)
                
            # Look for existing session for this case
            chat_session = ChatSession.query.filter_by(
                user_id=current_user.id,
                case_id=case.id
            ).first()
            
            if not chat_session:
                chat_session = ChatSession(
                    user_id=current_user.id,
                    case_id=case.id
                )
                db.session.add(chat_session)
                db.session.commit()
        else:
            # Look for general session without case
            chat_session = ChatSession.query.filter_by(
                user_id=current_user.id,
                case_id=None
            ).first()
            
            if not chat_session:
                chat_session = ChatSession(
                    user_id=current_user.id,
                    case_id=None
                )
                db.session.add(chat_session)
                db.session.commit()
        
        # Get chat history
        messages = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(ChatMessage.timestamp).all()
        
        # Get user's cases for context
        user_cases = Case.query.filter_by(user_id=current_user.id).all()
        
        return render_template('chat.html', session=chat_session, messages=messages, cases=user_cases)
    
    @app.route('/api/chat', methods=['POST'])
    @login_required
    def api_chat():
        data = request.json
        message = data.get('message')
        session_id = data.get('session_id')
        
        if not message or not session_id:
            return jsonify({'error': 'Missing message or session ID'}), 400
            
        # Get the chat session
        chat_session = ChatSession.query.get(session_id)
        if not chat_session or chat_session.user_id != current_user.id:
            return jsonify({'error': 'Invalid session'}), 403
            
        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            is_user=True,
            message=message
        )
        db.session.add(user_message)
        
        # Get context for AI response
        context = {}
        if chat_session.case_id:
            case = Case.query.get(chat_session.case_id)
            documents = Document.query.filter_by(case_id=case.id).all()
            context = {
                'case': case,
                'documents': documents
            }
            
        # Generate AI response
        ai_response = generate_ai_response(message, context)
        
        # Save AI response
        ai_message = ChatMessage(
            session_id=session_id,
            is_user=False,
            message=ai_response
        )
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({
            'response': ai_response,
            'user_message_id': user_message.id,
            'ai_message_id': ai_message.id
        })
    
    @app.route('/api/cases', methods=['POST'])
    @login_required
    def api_create_case():
        """API endpoint to create a new case."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
                
            title = data.get('title')
            category = data.get('category')
            
            if not title or not category:
                return jsonify({'error': 'Missing required fields'}), 400
                
            # Create a new case
            new_case = Case(
                user_id=current_user.id,
                title=title,
                category=category
            )
            db.session.add(new_case)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'case_id': new_case.id
            })
        except Exception as e:
            app.logger.error(f"Error creating case: {str(e)}")
            return jsonify({'error': 'Error creating case'}), 500
    
    @app.route('/api/document_upload', methods=['POST'])
    @login_required
    def api_document_upload():
        """API endpoint for regular (non-chunked) document uploads."""
        # Check if case_id exists
        case_id = request.form.get('case_id')
        if not case_id:
            return jsonify({'error': 'No case ID provided'}), 400
            
        case = Case.query.get_or_404(int(case_id))
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            # Create unique filename
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # Create user directory if it doesn't exist
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(user_dir, unique_filename)
            file.save(file_path)
            
            # Process document with OCR
            extracted_text, metadata = process_document(file_path, file_extension)
            
            # Save document info to database
            new_document = Document(
                user_id=current_user.id,
                case_id=case.id,
                filename=original_filename,
                file_path=file_path,
                file_type=file_extension,
                extracted_text=extracted_text,
                doc_metadata=metadata
            )
            db.session.add(new_document)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'document_id': new_document.id,
                'filename': original_filename
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    @app.route('/api/chunk_upload', methods=['POST'])
    @login_required
    def api_chunk_upload():
        """API endpoint for uploading a chunk of a large file."""
        try:
            # Check if case_id exists
            case_id = request.form.get('case_id')
            if not case_id:
                return jsonify({'error': 'No case ID provided'}), 400
                
            case = Case.query.get_or_404(int(case_id))
            
            # Check if user owns the case
            if case.user_id != current_user.id:
                return jsonify({'error': 'Unauthorized'}), 403
                
            # Get chunk information
            chunk_num = request.form.get('chunk')
            total_chunks = request.form.get('chunks')
            file_id = request.form.get('file_id')
            
            if not chunk_num or not total_chunks or not file_id:
                return jsonify({'error': 'Missing chunk information'}), 400
                
            # Check if file was uploaded
            if 'file' not in request.files:
                return jsonify({'error': 'No file chunk provided'}), 400
                
            file_chunk = request.files['file']
            
            # Create chunks directory
            chunks_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), 'chunks', file_id)
            os.makedirs(chunks_dir, exist_ok=True)
            
            # Save chunk
            chunk_path = os.path.join(chunks_dir, f"chunk_{chunk_num}")
            file_chunk.save(chunk_path)
            
            return jsonify({
                'success': True,
                'chunk': int(chunk_num),
                'total': int(total_chunks)
            })
        except Exception as e:
            app.logger.error(f"Error uploading chunk: {str(e)}")
            return jsonify({'error': f'Error uploading chunk: {str(e)}'}), 500
            
    @app.route('/api/complete_chunked_upload', methods=['POST'])
    @login_required
    def api_complete_chunked_upload():
        """API endpoint for completing a chunked file upload."""
        try:
            # Check if case_id exists
            case_id = request.form.get('case_id')
            if not case_id:
                return jsonify({'error': 'No case ID provided'}), 400
                
            case = Case.query.get_or_404(int(case_id))
            
            # Check if user owns the case
            if case.user_id != current_user.id:
                return jsonify({'error': 'Unauthorized'}), 403
                
            # Get file information
            file_id = request.form.get('file_id')
            file_name = request.form.get('file_name')
            file_type = request.form.get('file_type')
            total_chunks = int(request.form.get('chunks', '0'))
            
            if not file_id or not file_name or not total_chunks:
                return jsonify({'error': 'Missing file information'}), 400
                
            # Create unique filename
            original_filename = secure_filename(file_name)
            file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
            
            # Check file type
            if not allowed_file(original_filename):
                return jsonify({'error': 'Invalid file type'}), 400
                
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # Create user directory if it doesn't exist
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Path for the complete file
            complete_file_path = os.path.join(user_dir, unique_filename)
            
            # Chunks directory
            chunks_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), 'chunks', file_id)
            
            # Combine chunks
            with open(complete_file_path, 'wb') as outfile:
                for i in range(total_chunks):
                    chunk_path = os.path.join(chunks_dir, f"chunk_{i}")
                    if os.path.exists(chunk_path):
                        with open(chunk_path, 'rb') as infile:
                            outfile.write(infile.read())
                    else:
                        return jsonify({'error': f'Chunk {i} is missing'}), 400
            
            # Process document with OCR (only for smaller files, for large files defer processing)
            file_size = os.path.getsize(complete_file_path)
            extracted_text = ""
            metadata = {}
            
            # For files under 50MB, process immediately
            if file_size < 50 * 1024 * 1024:  # 50MB
                try:
                    extracted_text, metadata = process_document(complete_file_path, file_extension)
                except Exception as e:
                    app.logger.error(f"Error processing document: {str(e)}")
                    # Continue even if processing fails
            
            # Save document info to database
            new_document = Document(
                user_id=current_user.id,
                case_id=case.id,
                filename=original_filename,
                file_path=complete_file_path,
                file_type=file_extension,
                extracted_text=extracted_text,
                doc_metadata=metadata
            )
            db.session.add(new_document)
            db.session.commit()
            
            # Clean up chunks
            try:
                import shutil
                shutil.rmtree(chunks_dir)
            except Exception as e:
                app.logger.error(f"Error cleaning up chunks: {str(e)}")
                # Continue even if cleanup fails
            
            return jsonify({
                'success': True,
                'document_id': new_document.id,
                'filename': original_filename,
                'deferred_processing': file_size >= 50 * 1024 * 1024
            })
        except Exception as e:
            app.logger.error(f"Error completing upload: {str(e)}")
            return jsonify({'error': f'Error completing upload: {str(e)}'}), 500
    
    # Mailing service routes
    @app.route('/mail/<int:form_id>', methods=['GET', 'POST'])
    @login_required
    def mail_document(form_id):
        """
        Route for requesting a document to be mailed
        """
        form = GeneratedForm.query.get_or_404(form_id)
        case = Case.query.get_or_404(form.case_id)
        
        # Check if user owns the case
        if case.user_id != current_user.id:
            abort(403)
        
        # Check if document is paid for (clean version only)
        if current_user.subscription_type == 'free':
            flash('Please upgrade your subscription to use mailing services', 'warning')
            return redirect(url_for('pricing'))
        
        if current_user.subscription_type == 'pay_per_doc' and not form.is_paid:
            flash('Please purchase this document before requesting mailing services', 'warning')
            return redirect(url_for('pay_document', form_id=form.id))
        
        # Get existing mailing requests for this form
        existing_requests = MailingRequest.query.filter_by(
            user_id=current_user.id,
            generated_form_id=form_id
        ).order_by(MailingRequest.created_at.desc()).all()
        
        # Get available mailing options
        mailing_options = get_available_mailing_options()
        
        if request.method == 'POST':
            mail_type = request.form.get('mail_type')
            destination_type = request.form.get('destination_type')
            page_count = int(request.form.get('page_count', 1))
            include_copies = request.form.get('include_copies') == 'yes'
            copy_count = int(request.form.get('copy_count', 0)) if include_copies else 0
            
            # Get address information
            recipient_address = {
                'recipient_name': request.form.get('recipient_name'),
                'street_address': request.form.get('recipient_address_line1'),
                'unit': request.form.get('recipient_address_line2', ''),
                'city': request.form.get('recipient_city'),
                'province': request.form.get('recipient_province'),
                'postal_code': request.form.get('recipient_postal_code')
            }
            
            # Optional return address
            use_return_address = request.form.get('use_return_address') == 'yes'
            return_address = None
            if use_return_address:
                return_address = {
                    'recipient_name': request.form.get('return_name'),
                    'street_address': request.form.get('return_address_line1'),
                    'unit': request.form.get('return_address_line2', ''),
                    'city': request.form.get('return_city'),
                    'province': request.form.get('return_province'),
                    'postal_code': request.form.get('return_postal_code')
                }
            
            # Calculate cost
            cost_details = calculate_mailing_cost({
                'mail_type': mail_type, 
                'page_count': page_count, 
                'destination_type': destination_type, 
                'include_copies': include_copies, 
                'copy_count': copy_count
            })
            
            if not cost_details:
                flash('Error calculating mailing cost. Please try again.', 'danger')
                return redirect(url_for('mail_document', form_id=form_id))
            
            # Create mailing details
            mailing_details = {
                'mail_type': mail_type,
                'recipient_address': recipient_address,
                'return_address': return_address,
                'include_copies': include_copies,
                'copy_count': copy_count,
                'page_count': page_count,
                'destination_type': destination_type
            }
            
            # Create mailing request through utility function
            mailing_result = create_mailing_request(
                current_user.id,
                form_id,
                form.generated_file_path,
                mailing_details
            )
            
            if not mailing_result['success']:
                flash(f"Error creating mailing request: {mailing_result.get('error')}", 'danger')
                return redirect(url_for('mail_document', form_id=form_id))
            
            # Create database record
            mailing_request_data = mailing_result['mailing_request']
            recipient_addr = mailing_request_data['recipient_address']
            return_addr = mailing_request_data.get('return_address')
            
            mailing_request = MailingRequest(
                user_id=current_user.id,
                generated_form_id=form_id,
                reference_number=mailing_request_data['reference_number'],
                mail_type=mailing_request_data['mail_type'],
                status='pending',
                
                # Recipient address
                recipient_name=recipient_addr['recipient_name'],
                recipient_address_line1=recipient_addr['street_address'],
                recipient_address_line2=recipient_addr.get('unit', ''),
                recipient_city=recipient_addr['city'],
                recipient_province=recipient_addr['province'],
                recipient_postal_code=recipient_addr['postal_code'],
                
                # Mailing details
                include_copies=mailing_request_data['include_copies'],
                copy_count=mailing_request_data['copy_count'],
                page_count=page_count,
                destination_type=destination_type,
                cost_details=mailing_request_data['cost_details']
            )
            
            # Add return address if provided
            if return_addr:
                mailing_request.return_name = return_addr['recipient_name']
                mailing_request.return_address_line1 = return_addr['street_address']
                mailing_request.return_address_line2 = return_addr.get('unit', '')
                mailing_request.return_city = return_addr['city']
                mailing_request.return_province = return_addr['province']
                mailing_request.return_postal_code = return_addr['postal_code']
            
            db.session.add(mailing_request)
            db.session.commit()
            
            # Redirect to payment page
            return redirect(url_for('pay_mailing', mailing_id=mailing_request.id))
        
        return render_template(
            'mail_document.html',
            form=form,
            case=case,
            existing_requests=existing_requests,
            mailing_options=mailing_options
        )
    
    @app.route('/pay_mailing/<int:mailing_id>', methods=['GET', 'POST'])
    @login_required
    def pay_mailing(mailing_id):
        """
        Route for paying for a mailing request
        """
        # Import payment service
        from utils.payment_service import create_paypal_order, process_paypal_payment
        
        mailing_request = MailingRequest.query.get_or_404(mailing_id)
        
        # Check if user owns the mailing request
        if mailing_request.user_id != current_user.id:
            abort(403)
        
        # If already paid, redirect to mailing status
        if mailing_request.payment:
            return redirect(url_for('mailing_status', mailing_id=mailing_id))
        
        form = GeneratedForm.query.get_or_404(mailing_request.generated_form_id)
        case = Case.query.get_or_404(form.case_id)
        
        cost_details = mailing_request.cost_details
        total_cost = cost_details.get('total_cost', 0) if cost_details else 0
        
        # Initialize PayPal order
        paypal_order = None
        
        # Create a payment order if this is a GET request (initial page load)
        if request.method == 'GET':
            # Check if we have PayPal credentials
            if os.environ.get('PAYPAL_CLIENT_ID') and os.environ.get('PAYPAL_CLIENT_SECRET'):
                # Create a PayPal order for this mailing
                paypal_order = create_paypal_order(
                    amount=total_cost,
                    description=f"SmartDispute.ai - Mail Document: {mailing_request.mail_type.title()} Delivery"
                )
                
                if not paypal_order:
                    flash('Error creating payment. Please try again later.', 'danger')
            else:
                app.logger.warning("PayPal credentials not set in environment variables")
        
        # Process payment if this is a POST request
        if request.method == 'POST':
            payment_method = request.form.get('payment_method')
            
            if payment_method == 'paypal':
                paypal_order_id = request.form.get('paypal_order_id')
                
                if paypal_order_id:
                    # Process PayPal payment
                    payment_status = process_paypal_payment(paypal_order_id, total_cost)
                    
                    if payment_status == 'completed':
                        # Record payment
                        payment = Payment(
                            user_id=current_user.id,
                            amount=total_cost,
                            payment_type='mailing',
                            payment_method='paypal',
                            payment_id=paypal_order_id,
                            status='completed',
                            service_details={
                                'mailing_reference': mailing_request.reference_number,
                                'mail_type': mailing_request.mail_type,
                                'destination_type': mailing_request.destination_type,
                                'payment_date': datetime.utcnow().isoformat()
                            }
                        )
                        db.session.add(payment)
                        db.session.commit()
                        
                        # Update mailing request with payment ID and set to processing
                        mailing_request.payment_id = payment.id
                        mailing_request.status = 'processing'
                        db.session.commit()
                        
                        # Queue the mailing request for processing
                        queue_mailing_request(mailing_request)
                        
                        flash('Payment successful! Your document will be mailed shortly.', 'success')
                        return redirect(url_for('mailing_status', mailing_id=mailing_id))
                    else:
                        flash(f'Payment {payment_status}. Please try again.', 'danger')
            else:
                flash('Invalid payment method selected.', 'danger')
        
        return render_template(
            'pay_mailing.html',
            mailing_request=mailing_request,
            form=form,
            case=case,
            cost_details=cost_details,
            total_cost=total_cost,
            paypal_order=paypal_order
        )
    
    @app.route('/mailing_status/<int:mailing_id>')
    @login_required
    def mailing_status(mailing_id):
        """
        Route for checking the status of a mailing request
        """
        mailing_request = MailingRequest.query.get_or_404(mailing_id)
        
        # Check if user owns the mailing request
        if mailing_request.user_id != current_user.id:
            abort(403)
        
        form = GeneratedForm.query.get_or_404(mailing_request.generated_form_id)
        case = Case.query.get_or_404(form.case_id)
        
        # Get current status (in a real implementation, this would check with the mailing provider)
        current_status = get_mailing_request_status(mailing_request.reference_number)
        
        # Update status if changed
        if current_status and current_status.get('status') != mailing_request.status:
            mailing_request.status = current_status.get('status')
            if current_status.get('tracking_number'):
                mailing_request.tracking_number = current_status.get('tracking_number')
            if 'estimated_delivery' in current_status:
                mailing_request.estimated_delivery = datetime.fromisoformat(current_status['estimated_delivery'])
            db.session.commit()
        
        return render_template(
            'mailing_status.html',
            mailing_request=mailing_request,
            form=form,
            case=case,
            status_description=mailing_request.get_status_description()
        )
        
    @app.route('/my_mailings')
    @login_required
    def my_mailings():
        """
        Route for viewing all mailing requests
        """
        mailing_requests = MailingRequest.query.filter_by(
            user_id=current_user.id
        ).order_by(MailingRequest.created_at.desc()).all()
        
        return render_template('my_mailings.html', mailing_requests=mailing_requests)
    
    @app.route('/legal-updates')
    def legal_updates():
        """
        Route for displaying legal updates scraped from multiple Canadian legal sources
        """
        try:
            # Import the legal data scraper
            from utils.legal_data_scraper import LEGAL_SOURCES, analyze_source_updates, find_documents_by_keyword
            
            # Get source filter and search query
            source_filter = request.args.get('source', 'all')
            search_query = request.args.get('query', '').strip()
            
            # Prepare data directory
            data_dir = os.path.join(app.root_path, 'data/legal_source_data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Get analysis of recent updates
            try:
                analysis = analyze_source_updates(data_dir, days=30)
            except Exception as e:
                app.logger.error(f"Error analyzing source updates: {str(e)}")
                analysis = {source_id: {'documents': []} for source_id in LEGAL_SOURCES}
            
            # Search for documents if query provided
            search_results = []
            if search_query:
                try:
                    if source_filter == 'all':
                        search_results = find_documents_by_keyword(search_query, data_dir, max_results=20)
                    else:
                        # Search only in the selected source
                        source_data_dir = os.path.join(data_dir, source_filter)
                        if os.path.exists(source_data_dir):
                            search_results = find_documents_by_keyword(search_query, source_data_dir, max_results=20)
                except Exception as e:
                    app.logger.error(f"Error searching documents: {str(e)}")
            
            # Render template
            return render_template(
                'legal_updates.html',
                legal_sources=LEGAL_SOURCES,
                analysis=analysis,
                search_results=search_results
            )
            
        except Exception as e:
            app.logger.error(f"Error in legal_updates route: {str(e)}")
            flash(f"There was a problem loading the legal updates. Our team has been notified.", "warning")
            return redirect(url_for('index'))
        
    @app.route('/run-legal-scraper')
    @login_required
    def run_legal_scraper():
        """
        Route to trigger a legal data scrape (admin only)
        """
        if current_user.role != 'admin':
            flash('You do not have permission to run the legal scraper.', 'danger')
            return redirect(url_for('legal_updates'))
        
        # Import and run the scraper
        from utils.legal_data_scraper import LegalDataScraper
        
        try:
            # Create data directory
            data_dir = os.path.join(app.root_path, 'data/legal_source_data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Initialize and run the scraper
            scraper = LegalDataScraper(data_dir=data_dir)
            
            # Run the scraper in a background thread to avoid blocking
            def run_scraper_thread():
                try:
                    summary = scraper.run_scheduled_scrape()
                    app.logger.info(f"Legal scrape completed: {summary['total_documents']} documents from {summary['sources_scraped']} sources")
                except Exception as e:
                    app.logger.error(f"Error running legal scraper: {str(e)}")
            
            import threading
            thread = threading.Thread(target=run_scraper_thread)
            thread.daemon = True
            thread.start()
            
            flash(f'Legal data scrape started in the background. This may take several minutes.', 'info')
        except Exception as e:
            flash(f'Error starting legal scraper: {str(e)}', 'danger')
        
        return redirect(url_for('legal_updates'))

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
        
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

def init_admin_routes(app):
    @app.route('/admin/verifications')
    @login_required
    def admin_verifications():
        if current_user.role != 'admin':
            abort(403)
        
        pending_docs = VerificationDocument.query.filter_by(status='pending').all()
        return render_template('admin/verifications.html', documents=pending_docs)

    @app.route('/admin/verify/<int:doc_id>/<string:action>', methods=['POST'])
    @login_required
    def verify_document(doc_id, action):
        if current_user.role != 'admin':
            abort(403)
            
        doc = VerificationDocument.query.get_or_404(doc_id)
        doc.status = 'approved' if action == 'approve' else 'rejected'
        doc.reviewed_at = datetime.utcnow()
        doc.reviewed_by = current_user.id
        doc.review_notes = request.form.get('notes')
        
        user = User.query.get(doc.user_id)
        if action == 'approve':
            user.subscription_type = 'low_income'
            user.subscription_end = datetime.utcnow() + timedelta(days=365)
            flash('User verification approved and subscription updated', 'success')
        else:
            flash('Document rejected', 'info')
            
        db.session.commit()
        return redirect(url_for('admin_verifications'))

    @app.route('/api/create-payment-intent', methods=['POST'])
    def create_payment_intent():
        try:
            import stripe
            data = request.get_json()
            amount = data.get('amount')
            
            if not amount:
                return jsonify({'error': 'Amount is required'}), 400
                
            # Create a PaymentIntent with the order amount and currency
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency='cad',
                automatic_payment_methods={
                    'enabled': True,
                },
            )

            return jsonify({
                'clientSecret': payment_intent.client_secret
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
