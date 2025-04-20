import socket
import json
import threading
import queue
import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'mcp_server.log')),
        logging.StreamHandler()
    ]
)

class MCPServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # Dictionary to store client connections
        self.message_queue = queue.Queue()
        self.running = False
        
        # Create a separate log file for chat messages
        self.chat_logger = logging.getLogger('chat')
        self.chat_logger.setLevel(logging.INFO)
        chat_handler = logging.FileHandler(os.path.join('logs', 'chat_history.log'))
        chat_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.chat_logger.addHandler(chat_handler)
        
        # Create a separate log file for system messages
        self.system_logger = logging.getLogger('system')
        self.system_logger.setLevel(logging.INFO)
        system_handler = logging.FileHandler(os.path.join('logs', 'system.log'))
        system_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.system_logger.addHandler(system_handler)

    def start(self):
        """Start the MCP server"""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            logging.info(f"MCP Server started on {self.host}:{self.port}")

            # Start message processor thread
            processor_thread = threading.Thread(target=self.process_messages)
            processor_thread.daemon = True
            processor_thread.start()

            # Accept client connections
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    logging.info(f"New client connected from {address}")
                except Exception as e:
                    logging.error(f"Error accepting client connection: {e}")

        except Exception as e:
            logging.error(f"Server error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the MCP server"""
        self.running = False
        for client in self.clients.values():
            try:
                client.close()
            except:
                pass
        self.socket.close()
        logging.info("MCP Server stopped")

    def handle_client(self, client_socket, address):
        """Handle individual client connections"""
        try:
            while self.running:
                try:
                    # Receive message from client
                    data = client_socket.recv(4096)
                    if not data:
                        break

                    # Parse the message
                    message = json.loads(data.decode('utf-8'))
                    message['timestamp'] = datetime.now().isoformat()
                    message['client_address'] = address
                    
                    # Add to processing queue
                    self.message_queue.put(message)
                    
                    # Send acknowledgment
                    response = {
                        'status': 'received',
                        'timestamp': datetime.now().isoformat()
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))

                except json.JSONDecodeError:
                    logging.error(f"Invalid JSON received from {address}")
                except Exception as e:
                    logging.error(f"Error handling client {address}: {e}")
                    break

        finally:
            client_socket.close()
            if address in self.clients:
                del self.clients[address]
            logging.info(f"Client {address} disconnected")

    def process_messages(self):
        """Process messages from the queue"""
        while self.running:
            try:
                # Get message from queue
                message = self.message_queue.get(timeout=1)
                
                # Process message
                self.handle_message(message)
                
                # Mark task as done
                self.message_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error processing message: {e}")

    def handle_message(self, message):
        """Handle individual messages"""
        try:
            # Log message details
            logging.info(f"Processing message from {message['client_address']}")
            logging.info(f"Message type: {message.get('type', 'unknown')}")
            
            # Handle different message types
            if message.get('type') == 'chat':
                self.handle_chat_message(message)
            elif message.get('type') == 'system':
                self.handle_system_message(message)
            else:
                logging.warning(f"Unknown message type: {message.get('type')}")
                
        except Exception as e:
            logging.error(f"Error handling message: {e}")

    def handle_chat_message(self, message):
        """Handle chat messages"""
        try:
            # Log chat message with more details
            log_entry = {
                'timestamp': message.get('timestamp'),
                'client': str(message.get('client_address')),
                'content': message.get('content', ''),
                'type': 'user_message' if message.get('is_user', True) else 'ai_response'
            }
            self.chat_logger.info(json.dumps(log_entry))
            
            # Broadcast to other clients if needed
            self.broadcast_message({
                'type': 'chat',
                'sender': str(message['client_address']),
                'content': message.get('content', ''),
                'timestamp': message['timestamp']
            })
            
        except Exception as e:
            logging.error(f"Error handling chat message: {e}")

    def handle_system_message(self, message):
        """Handle system messages"""
        try:
            # Log system message with details
            log_entry = {
                'timestamp': message.get('timestamp'),
                'client': str(message.get('client_address')),
                'content': message.get('content', ''),
                'command': message.get('command')
            }
            self.system_logger.info(json.dumps(log_entry))
            
            # Handle system commands
            if message.get('command') == 'broadcast':
                self.broadcast_message(message)
                
        except Exception as e:
            logging.error(f"Error handling system message: {e}")

    def broadcast_message(self, message):
        """Broadcast message to all connected clients"""
        message_data = json.dumps(message).encode('utf-8')
        for client in self.clients.values():
            try:
                client.send(message_data)
            except Exception as e:
                logging.error(f"Error broadcasting message: {e}")

if __name__ == "__main__":
    # Create and start MCP server
    server = MCPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop() 