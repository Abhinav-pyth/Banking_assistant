from mcp_client import MCPClient
import time

def test_chat_logging():
    # Create and connect client
    client = MCPClient()
    if client.connect():
        print("Connected to MCP server")
        
        # Send test messages
        print("Sending test messages...")
        
        # Test user message
        client.send_chat_message("Hello, this is a test message from user", is_user=True)
        time.sleep(1)
        
        # Test assistant message
        client.send_chat_message("This is a test response from the assistant", is_user=False)
        time.sleep(1)
        
        # Test another user message
        client.send_chat_message("Can you help me with my banking needs?", is_user=True)
        time.sleep(1)
        
        print("Test messages sent. Check client_messages.log for the logged messages.")
        time.sleep(2)
        client.disconnect()
    else:
        print("Failed to connect to MCP server")

if __name__ == "__main__":
    test_chat_logging() 