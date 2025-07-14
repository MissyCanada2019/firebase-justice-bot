from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartDispute.ai</title>
        <style>
            body { font-family: Arial; text-align: center; margin-top: 50px; }
        </style>
    </head>
    <body>
        <h1>SmartDispute.ai - Simplified Server</h1>
        <p>This is a simplified server for SmartDispute.ai.</p>
        <p>Status: Running</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)