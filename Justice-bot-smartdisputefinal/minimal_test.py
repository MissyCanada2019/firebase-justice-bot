"""Minimal test Flask application"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "<h1>SmartDispute.ai Test Server</h1><p>Hello! This is a test server to check if Flask is working.</p>"

@app.route('/health')
def health_check():
    return {"status": "ok"}

if __name__ == '__main__':
    print("Starting minimal test server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
