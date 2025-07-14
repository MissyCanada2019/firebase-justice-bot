#!/usr/bin/env python3

import socket

# Check port 5000
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))
    print(f"Port 5000: {'OPEN' if result == 0 else 'CLOSED'} (result code: {result})")
    sock.close()
except Exception as e:
    print(f"Error checking port 5000: {e}")

# Check port 8080
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8080))
    print(f"Port 8080: {'OPEN' if result == 0 else 'CLOSED'} (result code: {result})")
    sock.close()
except Exception as e:
    print(f"Error checking port 8080: {e}")
