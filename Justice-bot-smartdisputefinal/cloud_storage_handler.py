"""
Cloud Storage Handler for SmartDispute.ai
Handles file downloads from Google Drive, OneDrive, and Dropbox
"""
import os
import requests
import tempfile
import logging
from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
import json
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

cloud_storage_bp = Blueprint('cloud_storage', __name__, url_prefix='/cloud')

# Supported file types for legal documents
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB per file

class CloudFileHandler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SmartDispute.ai/1.0'
        })

    def download_google_drive_file(self, file_info):
        """Download file from Google Drive using API"""
        try:
            file_id = file_info.get('id')
            if not file_id:
                raise ValueError("No file ID provided")

            # Get download URL for Google Drive
            download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
            
            # Get access token from session (from Google OAuth)
            access_token = session.get('google_access_token')
            if not access_token:
                raise ValueError("No Google access token available")

            headers = {'Authorization': f'Bearer {access_token}'}
            response = self.session.get(download_url, headers=headers, stream=True)
            
            if response.status_code == 200:
                return response.content, file_info.get('name', 'google_drive_file')
            else:
                raise Exception(f"Google Drive download failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Google Drive download error: {e}")
            raise

    def download_onedrive_file(self, file_info):
        """Download file from OneDrive"""
        try:
            download_url = file_info.get('downloadUrl') or file_info.get('@microsoft.graph.downloadUrl')
            if not download_url:
                raise ValueError("No download URL provided")

            response = self.session.get(download_url, stream=True)
            
            if response.status_code == 200:
                return response.content, file_info.get('name', 'onedrive_file')
            else:
                raise Exception(f"OneDrive download failed: {response.status_code}")

        except Exception as e:
            logger.error(f"OneDrive download error: {e}")
            raise

    def download_dropbox_file(self, file_info):
        """Download file from Dropbox"""
        try:
            download_url = file_info.get('link')
            if not download_url:
                raise ValueError("No download link provided")

            # Convert Dropbox share link to direct download
            if 'dropbox.com' in download_url:
                download_url = download_url.replace('?dl=0', '?dl=1')

            response = self.session.get(download_url, stream=True)
            
            if response.status_code == 200:
                return response.content, file_info.get('name', 'dropbox_file')
            else:
                raise Exception(f"Dropbox download failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Dropbox download error: {e}")
            raise

    def validate_file(self, filename, file_content):
        """Validate file type and size"""
        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type {file_ext} not allowed")

        # Check file size
        if len(file_content) > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {len(file_content)} bytes")

        return True

    def save_temp_file(self, file_content, filename):
        """Save file content to temporary location"""
        try:
            # Create secure filename
            secure_name = secure_filename(filename)
            
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, secure_name)
            
            with open(temp_path, 'wb') as f:
                f.write(file_content)
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Error saving temporary file: {e}")
            raise

@cloud_storage_bp.route('/download-files', methods=['POST'])
@login_required
def download_cloud_files():
    """Download files from cloud storage providers"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        cloud_files = data.get('cloud_files', {})
        downloaded_files = []
        handler = CloudFileHandler()

        for provider, files in cloud_files.items():
            if not files:
                continue

            for file_info_str in files:
                try:
                    file_info = json.loads(file_info_str) if isinstance(file_info_str, str) else file_info_str
                    
                    # Download based on provider
                    if provider == 'googledrive':
                        file_content, filename = handler.download_google_drive_file(file_info)
                    elif provider == 'onedrive':
                        file_content, filename = handler.download_onedrive_file(file_info)
                    elif provider == 'dropbox':
                        file_content, filename = handler.download_dropbox_file(file_info)
                    else:
                        logger.warning(f"Unknown provider: {provider}")
                        continue

                    # Validate file
                    handler.validate_file(filename, file_content)
                    
                    # Save to temporary location
                    temp_path = handler.save_temp_file(file_content, filename)
                    
                    downloaded_files.append({
                        'filename': filename,
                        'temp_path': temp_path,
                        'size': len(file_content),
                        'provider': provider
                    })

                except Exception as e:
                    logger.error(f"Error downloading file from {provider}: {e}")
                    continue

        if downloaded_files:
            # Store file paths in session for processing
            session['cloud_downloaded_files'] = downloaded_files
            
            return jsonify({
                'success': True,
                'files_downloaded': len(downloaded_files),
                'files': [{'filename': f['filename'], 'size': f['size']} for f in downloaded_files]
            })
        else:
            return jsonify({'error': 'No files could be downloaded'}), 400

    except Exception as e:
        logger.error(f"Cloud download error: {e}")
        return jsonify({'error': 'Failed to download files from cloud storage'}), 500

@cloud_storage_bp.route('/google-token', methods=['GET'])
@login_required
def get_google_token():
    """Get Google access token for Drive API"""
    try:
        # This would integrate with your Google OAuth system
        access_token = session.get('google_access_token')
        if access_token:
            return jsonify({'access_token': access_token})
        else:
            return jsonify({'error': 'No Google token available'}), 401
    except Exception as e:
        logger.error(f"Error getting Google token: {e}")
        return jsonify({'error': 'Failed to get Google token'}), 500

def init_cloud_storage(app):
    """Initialize cloud storage handler with Flask app"""
    app.register_blueprint(cloud_storage_bp)
    logger.info("Cloud storage handler initialized")