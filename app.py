from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
import markdown
from dotenv import load_dotenv
from mcp_client import MCPClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Configure Azure OpenAI
openai.api_type = "azure"
openai.api_base = os.getenv("ENDPOINT_URL")
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

# Initialize Flask and MCP Client
app = Flask(__name__)
CORS(app)

# Create MCP client instance
mcp_client = MCPClient()

def init_mcp():
    """Initialize MCP client connection"""
    if mcp_client.connect():
        mcp_client.register_handler('chat', handle_chat_response)
        logging.info("MCP client connected successfully")
    else:
        logging.error("Failed to connect to MCP server")

# Bank Information
BANK_INFO = {
    "name": "Global Trust Bank",
    "headquarters": "123 Financial District, New York, NY 10004",
    "phone": "1-800-GTB-BANK (1-800-482-2265)",
    "email": "support@globaltrust.com",
    "website": "www.globaltrustbank.com",
    "hours": {
        "weekdays": "9:00 AM - 5:00 PM EST",
        "saturday": "10:00 AM - 2:00 PM EST",
        "sunday": "Closed"
    },
    "branches": [
        "Manhattan Branch: 456 Wall Street, NY 10005",
        "Brooklyn Branch: 789 Atlantic Ave, Brooklyn, NY 11217",
        "Queens Branch: 321 Queens Blvd, Queens, NY 11101"
    ],
    "services": [
        "Personal Banking",
        "Business Banking",
        "Investment Services",
        "Mortgage Loans",
        "Credit Cards",
        "Online & Mobile Banking"
    ],
    "support_channels": {
        "online_banking": "onlinesupport@globaltrust.com",
        "technical_support": "tech.support@globaltrust.com",
        "customer_service": "customercare@globaltrust.com",
        "fraud_reporting": "fraud@globaltrust.com"
    }
}

# Banking chatbot system message
SYSTEM_MESSAGE = f"""You are an AI banking assistant for {BANK_INFO['name']}. You have access to the following bank information:
[Previous system message content...]"""

def handle_chat_response(message):
    """Handle chat responses from MCP server"""
    logging.info(f"Received chat response: {message}")
    # You can implement additional handling here

@app.route('/')
def home():
    # Initialize MCP connection if not already connected
    if not mcp_client.connected:
        init_mcp()
    return render_template('index.html', bank_info=BANK_INFO)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Ensure MCP connection
        if not mcp_client.connected:
            init_mcp()

        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Send message to MCP server
        mcp_client.send_chat_message(user_message)

        # Prepare the messages for chat completion
        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": user_message}
        ]

        # Generate the completion
        completion = openai.ChatCompletion.create(
            engine=os.getenv("DEPLOYMENT_NAME"),
            messages=messages,
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0.5,
            presence_penalty=0.5
        )

        # Get the response
        ai_response = completion.choices[0].message.content

        # Send AI response to MCP server
        mcp_client.send_chat_message(ai_response)

        # Convert markdown to HTML with extra features enabled
        ai_response_html = markdown.markdown(
            ai_response,
            extensions=['extra', 'smarty', 'tables']
        )

        return jsonify({'response': ai_response_html})

    except Exception as e:
        logging.error(f"Error details: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request. Please try again later.'}), 500

@app.teardown_appcontext
def cleanup(exception=None):
    """Cleanup when the app context ends"""
    mcp_client.disconnect()

if __name__ == '__main__':
    # Initialize MCP connection before starting the app
    init_mcp()
    app.run(debug=True) 