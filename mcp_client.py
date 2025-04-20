import socket
import json
import threading
import logging
import os
from queue import Queue
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'mcp_client.log')),
        logging.StreamHandler()
    ]
)

class MCPClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.message_queue = Queue()
        self.response_handlers = {}
        self.running = False
        
        # Create a separate log file for message history with JSON formatting
        self.message_logger = logging.getLogger('messages')
        self.message_logger.setLevel(logging.INFO)
        message_handler = logging.FileHandler(os.path.join('logs', 'client_messages.log'))
        formatter = logging.Formatter('%(message)s')
        message_handler.setFormatter(formatter)
        self.message_logger.addHandler(message_handler)
        # Prevent duplicate logging
        self.message_logger.propagate = False

    def connect(self):
        """Connect to the MCP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.running = True

            # Start receiver thread
            receiver_thread = threading.Thread(target=self.receive_messages)
            receiver_thread.daemon = True
            receiver_thread.start()

            logging.info(f"Connected to MCP server at {self.host}:{self.port}")
            return True

        except Exception as e:
            logging.error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from the MCP server"""
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        logging.info("Disconnected from MCP server")

    def send_message(self, message_type, content, **kwargs):
        """Send a message to the MCP server"""
        if not self.connected:
            logging.error("Not connected to MCP server")
            return False

        try:
            message = {
                'type': message_type,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                **kwargs
            }

            # Only log in send_chat_message, not here
            self.socket.send(json.dumps(message).encode('utf-8'))
            logging.info(f"Sent {message_type} message to server")
            return True

        except Exception as e:
            logging.error(f"Error sending message: {e}")
            self.disconnect()
            return False

    def send_chat_message(self, content, is_user=True):
        """Send a chat message"""
        timestamp = datetime.now().isoformat()
        
        # Log the chat message before sending
        log_entry = {
            'timestamp': timestamp,
            'direction': 'outgoing',
            'type': 'chat',
            'sender': 'user' if is_user else 'assistant',
            'content': content
        }
        self.message_logger.info(json.dumps(log_entry))
        
        return self.send_message('chat', content, is_user=is_user, timestamp=timestamp)

    def send_system_message(self, content, command=None):
        """Send a system message"""
        return self.send_message('system', content, command=command)

    def receive_messages(self):
        """Receive messages from the server"""
        while self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break

                message = json.loads(data.decode('utf-8'))
                self.handle_message(message)

            except json.JSONDecodeError:
                logging.error("Received invalid JSON data")
            except Exception as e:
                logging.error(f"Error receiving message: {e}")
                break

        self.disconnect()

    def handle_message(self, message):
        """Handle received messages"""
        try:
            timestamp = datetime.now().isoformat()
            message_type = message.get('type')
            
            # Create detailed log entry
            log_entry = {
                'timestamp': timestamp,
                'direction': 'incoming',
                'type': message_type,
                'sender': message.get('sender', 'unknown'),
                'content': message.get('content', '')
            }
            
            # Only log chat messages to client_messages.log
            if message_type == 'chat':
                self.message_logger.info(json.dumps(log_entry))
            
            # Process message handlers
            if message_type in self.response_handlers:
                self.response_handlers[message_type](message)
            else:
                self.message_queue.put(message)
                logging.info(f"Received message: {message}")

        except Exception as e:
            logging.error(f"Error handling message: {e}")

    def register_handler(self, message_type, handler):
        """Register a message handler for a specific message type"""
        self.response_handlers[message_type] = handler

    def get_next_message(self, timeout=None):
        """Get the next message from the queue"""
        try:
            return self.message_queue.get(timeout=timeout)
        except:
            return None 