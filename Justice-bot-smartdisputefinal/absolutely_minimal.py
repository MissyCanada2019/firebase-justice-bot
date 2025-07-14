"""
Absolutely minimal Flask application 
for SmartDispute.ai troubleshooting
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
        <head>
            <title>SmartDispute.ai - Minimal Test</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 800px; 
                    margin: 40px auto; 
                    padding: 20px;
                    line-height: 1.6;
                }
                h1 { color: #2c3e50; }
                .card {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    background-color: #f9f9f9;
                }
            </style>
        </head>
        <body>
            <h1>SmartDispute.ai - Minimal Test Page</h1>
            <div class="card">
                <h2>Test successful!</h2>
                <p>This minimal Flask application is working correctly.</p>
                <p>If you can see this page, the basic web server configuration is functional.</p>
                <p>We can now work on restoring the full application.</p>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    print("Starting minimal Flask application on port 5000...")
    app.run(host='0.0.0.0', port=5000)
