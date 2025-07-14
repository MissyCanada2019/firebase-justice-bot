#!/usr/bin/env python3
# Server diagnostic tool for SmartDispute.ai

import os
import sys
import socket
import http.client
import subprocess
import time

# Configuration
HOSTS = ['localhost', '0.0.0.0', '127.0.0.1']
PORTS = [5000, 8080]

# Test HTTP endpoints to check
TEST_ENDPOINTS = [
    '/health',   # Health check endpoint
    '/',         # Main page
    '/login',    # Login page
]

def check_port_open(host, port):
    """Check if a TCP port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)  # 3 second timeout
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0   # 0 means port is open
    except Exception as e:
        print(f"Error checking {host}:{port} - {str(e)}")
        return False

def make_http_request(host, port, path):
    """Make an HTTP request to an endpoint"""
    try:
        conn = http.client.HTTPConnection(host, port, timeout=5)
        conn.request("GET", path)
        res = conn.getresponse()
        data = res.read().decode('utf-8')[:100]  # First 100 chars only
        conn.close()
        return res.status, data
    except Exception as e:
        return None, str(e)

def get_listening_processes():
    """Get processes listening on TCP ports"""
    try:
        output = subprocess.check_output(["netstat", "-tulpn"], stderr=subprocess.STDOUT, text=True)
        return output
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            output = subprocess.check_output(["ss", "-tulpn"], stderr=subprocess.STDOUT, text=True)
            return output
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "Unable to determine listening processes - netstat and ss not available"

def check_replit_domains():
    """Check Replit domain environment variables"""
    replit_domains = os.environ.get("REPLIT_DOMAINS")
    replit_dev_domain = os.environ.get("REPLIT_DEV_DOMAIN")
    replit_deployment = os.environ.get("REPLIT_DEPLOYMENT")
    
    print("\nReplit Domain Information:")
    print(f"REPLIT_DOMAINS: {replit_domains or 'Not set'}")
    print(f"REPLIT_DEV_DOMAIN: {replit_dev_domain or 'Not set'}")
    print(f"REPLIT_DEPLOYMENT: {replit_deployment or 'Not set'}")
    
    if replit_domains:
        domains = replit_domains.split(",")
        print(f"Available domains: {domains}")
    
def main():
    print("SmartDispute.ai Server Diagnostics")
    print("=================================\n")
    
    # Check if ports are open
    print("Port Availability:")
    for host in HOSTS:
        for port in PORTS:
            is_open = check_port_open(host, port)
            print(f"{host}:{port} - {'Open' if is_open else 'Closed'}")
    
    # Make HTTP requests
    print("\nHTTP Endpoints:")
    for host in ['localhost', '127.0.0.1']:
        for port in PORTS:
            if check_port_open(host, port):
                for path in TEST_ENDPOINTS:
                    status, data = make_http_request(host, port, path)
                    print(f"{host}:{port}{path} - {status or 'Error'} - {data[:50] if status else data}")
    
    # Get listening processes
    print("\nListening Processes:")
    processes = get_listening_processes()
    print(processes)
    
    # Check Replit domains
    check_replit_domains()

if __name__ == "__main__":
    main()
