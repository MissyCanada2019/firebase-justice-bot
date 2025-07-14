"""
Port Detector for SmartDispute.ai

This script will:
1. Print all relevant Replit environment variables
2. Test port bindings on both 5000 and 8080
3. Identify any proxy configuration issues
4. Create a diagnostic report
"""
import os
import socket
import sys
import json
import logging
import subprocess
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('port_detector')

# HTML template for the diagnostic page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SmartDispute.ai - Port Diagnostic</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #222; color: #eee; }
        h1 { color: #e62e2e; }
        .container { border: 1px solid #444; padding: 20px; border-radius: 5px; max-width: 800px; margin: 0 auto; }
        .success { color: #4CAF50; }
        .warning { color: #FFA500; }
        .error { color: #e62e2e; }
        pre { background-color: #333; padding: 10px; border-radius: 5px; overflow-x: auto; }
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            margin-right: 5px;
            font-weight: bold;
        }
        .port-5000 { background-color: #3498db; }
        .port-8080 { background-color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <h1>SmartDispute.ai Port Diagnostic</h1>
        <div>
            <span class="badge port-5000">PORT 5000</span>
            <span class="badge port-8080">PORT 8080</span>
            You accessed this via: <strong>{{SERVER_PORT}}</strong>
        </div>
        
        <h2>Environment Variables</h2>
        <pre>{{ENV_VARS}}</pre>
        
        <h2>Port Bindings</h2>
        <pre>{{PORT_STATUS}}</pre>
        
        <h2>Server Information</h2>
        <pre>{{SERVER_INFO}}</pre>
        
        <h2>External Accessibility</h2>
        <pre>{{EXTERNAL_ACCESS}}</pre>
        
        <h2>Recommendations</h2>
        <div class="{{RECOMMENDATION_CLASS}}">
            {{RECOMMENDATIONS}}
        </div>
    </div>
</body>
</html>
"""

class DiagnosticHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the port diagnostic tool"""
    
    def log_message(self, format, *args):
        """Override to use our logger instead"""
        logger.info("%s - %s", self.address_string(), format % args)
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Get server port
        server_port = self.server.server_port
        
        # Collect environment variables
        env_vars = {}
        for key in sorted(os.environ.keys()):
            if key.startswith('REPLIT') or key in ['PORT', 'HTTP_PORT', 'HTTPS_PORT']:
                env_vars[key] = os.environ[key]
        
        # Check port status
        port_status = check_port_bindings()
        
        # Get server info
        server_info = {
            'Python Version': sys.version,
            'Server Address': self.server.server_address,
            'Client Address': self.client_address,
            'Request Path': self.path,
            'Headers': dict(self.headers),
        }
        
        # Test external accessibility
        external_access = check_external_access()
        
        # Generate recommendations
        recommendation_class = 'warning'
        recommendations = []
        
        if not port_status['5000']['available']:
            recommendations.append('Port 5000 is already in use. Try using port 8080 instead.')
        
        if not port_status['8080']['available']:
            recommendations.append('Port 8080 is already in use. Try using a different port.')
        
        if not external_access['reachable']:
            recommendations.append(
                'The server does not appear to be externally accessible. '
                'Check Replit proxy settings and make sure your app is binding to 0.0.0.0.'
            )
            recommendation_class = 'error'
        else:
            recommendations.append(
                'The server appears to be accessible! If you are still having issues, '
                'try the suggestions below.'
            )
            recommendation_class = 'success'
        
        recommendations.append(
            'Make sure your Flask app is binding to 0.0.0.0 and not localhost.'
        )
        recommendations.append(
            'Try using port 8080 instead of 5000, as some proxies might prefer it.'
        )
        recommendations.append(
            'Check your .replit file to ensure the port forwarding is configured correctly.'
        )
        
        # Fill in the template
        html = HTML_TEMPLATE
        html = html.replace('{{SERVER_PORT}}', str(server_port))
        html = html.replace('{{ENV_VARS}}', json.dumps(env_vars, indent=2))
        html = html.replace('{{PORT_STATUS}}', json.dumps(port_status, indent=2))
        html = html.replace('{{SERVER_INFO}}', json.dumps(server_info, indent=2))
        html = html.replace('{{EXTERNAL_ACCESS}}', json.dumps(external_access, indent=2))
        html = html.replace('{{RECOMMENDATION_CLASS}}', recommendation_class)
        html = html.replace('{{RECOMMENDATIONS}}', '<ul>' + ''.join([f'<li>{r}</li>' for r in recommendations]) + '</ul>')
        
        self.wfile.write(html.encode())

def check_port_bindings():
    """Check what ports are available or in use"""
    results = {
        '5000': {'available': False, 'process': None},
        '8080': {'available': False, 'process': None}
    }
    
    # Check port 5000
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 5000))
        if result == 0:
            # Port is in use
            results['5000']['available'] = False
            # Try to get the process using this port
            try:
                output = subprocess.check_output(['lsof', '-i', ':5000']).decode()
                results['5000']['process'] = output.strip()
            except:
                results['5000']['process'] = "Unknown (couldn't determine process)"
        else:
            # Port is available
            results['5000']['available'] = True
        sock.close()
    except:
        results['5000']['available'] = False
        results['5000']['process'] = "Error checking port"
    
    # Check port 8080
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 8080))
        if result == 0:
            # Port is in use
            results['8080']['available'] = False
            # Try to get the process using this port
            try:
                output = subprocess.check_output(['lsof', '-i', ':8080']).decode()
                results['8080']['process'] = output.strip()
            except:
                results['8080']['process'] = "Unknown (couldn't determine process)"
        else:
            # Port is available
            results['8080']['available'] = True
        sock.close()
    except:
        results['8080']['available'] = False
        results['8080']['process'] = "Error checking port"
    
    return results

def check_external_access():
    """Check if the server is accessible from outside"""
    result = {
        'reachable': False,
        'url': None,
        'error': None
    }
    
    # Get the Replit domain
    replit_domain = os.environ.get('REPLIT_DEV_DOMAIN')
    if not replit_domain:
        result['error'] = "REPLIT_DEV_DOMAIN environment variable not set"
        return result
    
    # Try to access the server externally
    url = f"https://{replit_domain}/"
    result['url'] = url
    
    try:
        response = urllib.request.urlopen(url, timeout=5)
        result['reachable'] = response.status == 200
        result['status'] = response.status
        result['headers'] = dict(response.headers)
    except Exception as e:
        result['error'] = str(e)
    
    return result

def run_diagnostic_server_port_5000():
    """Run the diagnostic server on port 5000"""
    try:
        server = HTTPServer(('0.0.0.0', 5000), DiagnosticHandler)
        logger.info(f"Started diagnostic server on port 5000")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start diagnostic server on port 5000: {e}")

def run_diagnostic_server_port_8080():
    """Run the diagnostic server on port 8080"""
    try:
        server = HTTPServer(('0.0.0.0', 8080), DiagnosticHandler)
        logger.info(f"Started diagnostic server on port 8080")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start diagnostic server on port 8080: {e}")

def main():
    """Main entry point"""
    logger.info("Starting SmartDispute.ai Port Detector")
    
    # Log environment variables
    logger.info("Replit Environment Variables:")
    for key in sorted(os.environ.keys()):
        if key.startswith('REPLIT'):
            logger.info(f"  {key} = {os.environ[key]}")
    
    # Check port bindings
    port_status = check_port_bindings()
    logger.info(f"Port 5000 status: {'Available' if port_status['5000']['available'] else 'In use'}")
    logger.info(f"Port 8080 status: {'Available' if port_status['8080']['available'] else 'In use'}")
    
    # Start diagnostic servers
    logger.info("Starting diagnostic servers on ports 5000 and 8080")
    
    # Try to start on port 8080 first
    port_8080_thread = threading.Thread(target=run_diagnostic_server_port_8080)
    port_8080_thread.daemon = True
    port_8080_thread.start()
    
    # Then try port 5000 on the main thread
    run_diagnostic_server_port_5000()

if __name__ == "__main__":
    main()