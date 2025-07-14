#!/usr/bin/env python3
"""
TCP Port Forwarder for SmartDispute.ai

A lightweight socket-based TCP port forwarder that forwards traffic
from port 8080 to port 5000 without any dependencies.

This uses raw sockets rather than HTTP parsing, so it works with any protocol.
"""
import socket
import select
import time
import threading
import sys
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tcp_port_forward.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("port_forwarder")

# Configuration
LOCAL_PORT = 8080
REMOTE_PORT = 5000
BUFFER_SIZE = 4096
MAX_CONNECTIONS = 20

connections = []
total_connections = 0


def forward_data(source, destination):
    """Forward data from source to destination"""
    try:
        data = source.recv(BUFFER_SIZE)
        if data:
            destination.sendall(data)
            return len(data)
        return 0
    except socket.error as e:
        logger.error(f"Socket error while forwarding data: {e}")
        return -1


def handle_connection(client_socket, client_address):
    """Handle a client connection by forwarding to the target"""
    global total_connections
    
    try:
        logger.info(f"New connection from {client_address}")
        
        # Connect to target server
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect(('localhost', REMOTE_PORT))
        
        # Forward data in both directions
        total_bytes_forwarded = 0
        while True:
            # Wait for data on either socket
            readable, _, exceptional = select.select([client_socket, target_socket], [], [client_socket, target_socket], 1)
            
            if client_socket in exceptional or target_socket in exceptional:
                logger.warning("Connection problem detected")
                break
                
            if client_socket in readable:
                bytes_forwarded = forward_data(client_socket, target_socket)
                if bytes_forwarded <= 0:
                    break
                total_bytes_forwarded += bytes_forwarded
                
            if target_socket in readable:
                bytes_forwarded = forward_data(target_socket, client_socket)
                if bytes_forwarded <= 0:
                    break
                total_bytes_forwarded += bytes_forwarded
                
        logger.info(f"Connection closed, forwarded {total_bytes_forwarded} bytes")
                
    except Exception as e:
        logger.error(f"Error handling connection: {e}")
        
    finally:
        # Clean up
        if 'client_socket' in locals() and client_socket:
            client_socket.close()
        if 'target_socket' in locals() and target_socket:
            target_socket.close()


def main():
    """Main function that sets up the server and handles connections"""
    global connections
    global total_connections
    
    # Create server socket
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setblocking(False)  # Set non-blocking mode
        server.bind(('0.0.0.0', LOCAL_PORT))
        server.listen(MAX_CONNECTIONS)
        
        logger.info(f"=== SmartDispute.ai TCP Port Forwarder ===")
        logger.info(f"Forwarding connections from port {LOCAL_PORT} to port {REMOTE_PORT}")
        logger.info(f"Server started on 0.0.0.0:{LOCAL_PORT}")
        
        # Save PID to file
        with open('tcp_port_forward.pid', 'w') as f:
            f.write(str(os.getpid()))
        
        # Main loop
        while True:
            try:
                # Accept new connections
                readable, _, _ = select.select([server], [], [], 1)
                
                if server in readable:
                    client_socket, client_address = server.accept()
                    client_socket.setblocking(False)
                    
                    # Start a new thread to handle the connection
                    t = threading.Thread(target=handle_connection, args=(client_socket, client_address))
                    t.daemon = True
                    t.start()
                    
                    connections.append(t)
                    total_connections += 1
                    
                    # Clean up completed threads
                    connections = [t for t in connections if t.is_alive()]
                    
                    logger.info(f"Active connections: {len(connections)}, Total handled: {total_connections}")
                
                # Small sleep to prevent CPU overload    
                time.sleep(0.01)
                
            except KeyboardInterrupt:
                logger.info("Shutting down server...")
                break
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        return 1
        
    finally:
        # Clean up
        if 'server' in locals():
            server.close()
            
    return 0


if __name__ == "__main__":
    sys.exit(main())