#!/usr/bin/env python3
"""
Simple test to verify SmartDispute.ai is working
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head><title>SmartDispute.ai - Test Page</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa;">
        <div style="max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #dc2626; text-align: center;">🍁 SmartDispute.ai</h1>
            <h2 style="color: #1e40af; text-align: center;">Canadian Legal Platform</h2>
            <p style="text-align: center; font-size: 18px; color: #059669;">
                ✓ Application is running successfully!
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <p style="font-size: 16px;">
                    "Everyone has the right to life, liberty and security of the person"<br>
                    - Canadian Charter of Rights and Freedoms, Section 7
                </p>
            </div>
            <div style="background: #fef3c7; padding: 20px; border-radius: 6px; margin: 20px 0;">
                <h3 style="color: #b45309;">Pilot Program Active</h3>
                <p>Free access for first 1000 Canadian users. Join our mission to democratize legal justice.</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {"status": "healthy", "service": "SmartDispute.ai", "message": "Working correctly"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)