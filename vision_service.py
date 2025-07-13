# vision_service.py

import base64
import os
from google.cloud import vision_v1p3beta1 as vision
from flask import Flask, request, jsonify, session, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS
from dotenv import load_dotenv
from google.cloud import firestore
import uuid
from datetime import datetime
from docx import Document
import json

# Load environment variables from .env file
load_dotenv()

# Configure Flask
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key')
CORS(app)

# Initialize Google Cloud Vision client
client = vision.ImageAnnotatorClient()
def analyze_document_text(image_content: bytes):
    """
    Analyzes document text from image content using Google Cloud Vision API.
    """
    image = vision.Image(content=image_content)
    response = client.document_text_detection(image=image)
    return response.full_text_annotation.text if response.full_text_annotation else ""

def classify_document(image_content: bytes):
    text = analyze_document_text(image_content)
    text = text.lower()
    if "notice to end tenancy" in text or "n4 form" in text:
        return "N4 – Notice to End Tenancy"
    elif "eviction order" in text:
        return "Eviction Order"
    elif "children's aid society" in text or "cas report" in text:
        return "CAS Report"
    elif "police notice" in text:
        return "Police Notice"
    elif "pay stub" in text or "paycheck" in text:
        return "Pay Stub"
    elif "screenshot" in text and ("text" in text or "message" in text):
        return "Text Screenshot Evidence"
    else:
        return "Unknown Document Type"

# Example usage (for testing)
if __name__ == '__main__':
    # Replace 'your_image.jpg' with the path to a test image file
    # Or replace with a path to a PDF if your setup handles PDF conversion to image
    image_path = 'your_image.jpg' # Or path to your test file

    if os.path.exists(image_path):
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()

            text = analyze_document_text(content)
            print("Extracted Text:")
            print(text)

            doc_type = classify_document(content)
            print("Document Type:")
            print(doc_type)

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please ensure you have Google Cloud credentials set up correctly (GOOGLE_APPLICATION_CREDENTIALS environment variable).")
            print("Also, ensure the file path is correct and it's a supported image format.")
    else:
        print(f"Error: Test file not found at {image_path}")
        print("Please replace 'your_image.jpg' with the path to a valid file for testing.")


UPLOAD_FOLDER = os.path.abspath('uploads') # Use absolute path
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Firestore client
db = firestore.Client()

app.static_folder = UPLOAD_FOLDER
app.add_url_rule('/static/forms/<filename>', endpoint='static', view_func=app.send_static_file)

@app.route('/api/vision/extract', methods=['POST'])
def extract_text_and_classify_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    # Use absolute path for saving
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    with open(filepath, 'rb') as image_file:
        content = image_file.read()

    full_text = analyze_document_text(content)
    # Pass content bytes to classify_document
    document_type = classify_document(content)
    evidence_id = str(uuid.uuid4())
    upload_date = datetime.utcnow().isoformat()

    # Create evidence record
    evidence = {
        "id": evidence_id,
        "filename": filename,
        "document_type": document_type,
        "extracted_text": full_text,
        "upload_date": upload_date
    }

    # Store in session
    session.setdefault("case_profile", {})
    session["case_profile"].setdefault("evidence", []).append(evidence)
    session.modified = True

    # Store in Firestore
    db.collection("evidence").document(evidence_id).set(evidence)

    os.remove(filepath)

    return jsonify({
        'message': 'File uploaded and processed successfully',
        'evidence': evidence,
        'case_profile': session["case_profile"]
    })

@app.route('/api/case/profile', methods=['GET'])
def get_case_profile():
    return jsonify(session.get("case_profile", {"evidence": []}))

@app.route('/api/case/clear', methods=['POST'])
def clear_case_profile():
    session.pop("case_profile", None)
    session.modified = True
    return jsonify({"message": "Case profile cleared"})

@app.route('/api/forms', methods=['GET'])
def get_forms():
    try:
        # Use absolute path for accessing forms.json
        forms_path = os.path.abspath('data/forms.json')
        with open(forms_path, 'r') as f:
            forms_data = json.load(f)
        return jsonify(forms_data)
    except FileNotFoundError:
        return jsonify({'error': f'forms.json not found at {forms_path}'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Error decoding forms.json'}), 500

if __name__ == '__main__':
    app.run(debug=True)
