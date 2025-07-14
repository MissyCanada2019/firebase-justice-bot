"""
Quick deployment script for SmartDispute.ai
This is a minimal version designed to work with Replit's hosting environment
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartDispute.ai - Quick Deploy</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; }
            .status { 
                margin-top: 20px;
                padding: 10px;
                background-color: #e8f5e9;
                border-left: 4px solid #4caf50;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SmartDispute.ai</h1>
            <p>Empowering Canadians with AI-powered legal tools.</p>
            <div class="status">
                <strong>Status:</strong> Server is operational
            </div>
            <p>This is a quick deployment version of the SmartDispute.ai application.</p>
            <p>Once this page is working, we can safely transition to the full application.</p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)