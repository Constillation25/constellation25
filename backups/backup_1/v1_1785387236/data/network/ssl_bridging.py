#!/data/data/com.termux/files/usr/bin/python3
"""
SSL Bridging Load Balancer
Users → [Encrypted] → Load Balancer → [Decrypted] → [Re-encrypted with different cert] → Backend
"""
import ssl
import socket
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import URLError

logging.basicConfig(level=logging.INFO, format='%(asctime)s [SSL-BRIDGE] %(message)s')
logger = logging.getLogger(__name__)

class SSLBridgingProxy:
    """
    SSL Bridging: Terminates SSL at load balancer, re-encrypts to backend
    with a DIFFERENT certificate (backend has its own SSL cert)
    """
    def __init__(self, listen_port=8443, backend_host='localhost', backend_port=8444,
                 lb_cert_path=None, lb_key_path=None):
        self.listen_port = listen_port
        self.backend_host = backend_host
        self.backend_port = backend_port
        self.lb_cert_path = lb_cert_path
        self.lb_key_path = lb_key_path
        self.running = False

    def handle_client(self, client_socket, client_addr):
        """Handle incoming HTTPS client connection"""
        try:
            # Wrap client socket with LB's SSL certificate
            if self.lb_cert_path and self.lb_key_path:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(self.lb_cert_path, self.lb_key_path)
                client_socket = context.wrap_socket(client_socket, server_side=True)

            # Receive request from client
            request = client_socket.recv(4096).decode('utf-8', errors='ignore')
            if not request:
                return

            logger.info(f"Client {client_addr} → LB: {request[:80]}...")

            # Forward to backend with RE-ENCRYPTION (backend has different cert)
            backend_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            backend_context.check_hostname = False
            backend_context.verify_mode = ssl.CERT_NONE

            backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            backend_socket = backend_context.wrap_socket(backend_socket, server_hostname=self.backend_host)
            backend_socket.connect((self.backend_host, self.backend_port))

            # Send decrypted request to backend (re-encrypted with backend's cert)
            backend_socket.sendall(request.encode('utf-8'))
            logger.info(f"LB → Backend {self.backend_host}:{self.backend_port} (re-encrypted)")

            # Receive response from backend
            response = b""
            while True:
                try:
                    chunk = backend_socket.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break

            backend_socket.close()
            logger.info(f"Backend → LB: {len(response)} bytes")

            # Send response back to client
            client_socket.sendall(response)
            logger.info(f"LB → Client {client_addr}: {len(response)} bytes")

        except Exception as e:
            logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass

    def start(self):
        """Start the SSL bridging proxy"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.listen_port))
        server_socket.listen(10)
        self.running = True

        logger.info(f"SSL Bridging Proxy started on port {self.listen_port}")
        logger.info(f"Backend: {self.backend_host}:{self.backend_port}")
        logger.info("Traffic flow: Client[HTTPS] → LB[decrypt] → LB[re-encrypt] → Backend[HTTPS]")

        while self.running:
            try:
                client_socket, client_addr = server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_socket, client_addr))
                thread.daemon = True
                thread.start()
            except Exception as e:
                if self.running:
                    logger.error(f"Accept error: {e}")

    def stop(self):
        self.running = False

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8443
    backend = sys.argv[2] if len(sys.argv) > 2 else 'localhost:8444'
    host, bport = backend.split(':') if ':' in backend else (backend, '8444')

    proxy = SSLBridgingProxy(
        listen_port=port,
        backend_host=host,
        backend_port=int(bport)
    )

    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.stop()
        logger.info("SSL Bridging Proxy stopped")
