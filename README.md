# Banking Chatbot with MCP Integration

A sophisticated banking chatbot application that uses Azure OpenAI and Model Context Protocol (MCP) for secure and efficient message handling.

## Features

- **AI-Powered Banking Assistant**: Uses Azure OpenAI to provide intelligent responses to banking queries
- **Model Context Protocol (MCP)**: Implements a secure message communication protocol
- **Real-time Chat Interface**: Modern, responsive UI for seamless user interaction
- **Comprehensive Logging**: Detailed logging system for monitoring and debugging
- **Bank Information Integration**: Dynamic display of bank details and services
- **Markdown Support**: Rich text formatting for responses

## Project Structure

```
.
├── app.py                  # Main Flask application
├── mcp_server.py          # MCP server implementation
├── mcp_client.py          # MCP client implementation
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── templates/             # HTML templates
│   └── index.html        # Chat interface
├── static/               # Static files (CSS, JS)
└── logs/                 # Log files
    ├── client_messages.log
    ├── mcp_client.log
    └── mcp_server.log
```

## Prerequisites

- Python 3.8 or higher
- Azure OpenAI API access
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd banking-chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your credentials:
   ```
   ENDPOINT_URL=your_azure_endpoint
   AZURE_OPENAI_API_KEY=your_api_key
   DEPLOYMENT_NAME=your_deployment_name
   ```

## Usage

1. Start the MCP server:
   ```bash
   python mcp_server.py
   ```

2. In a new terminal, start the Flask application:
   ```bash
   python app.py
   ```

3. Access the chatbot interface at `http://localhost:5000`

## MCP Protocol

The Model Context Protocol (MCP) is implemented to handle message communication between the chatbot and the server. It provides:

- Secure message transmission
- Message queuing and reliability
- Detailed logging
- Real-time message handling

### Message Types

- **Chat Messages**: User queries and AI responses
- **System Messages**: Administrative and control messages

## Logging

The application maintains detailed logs in the `logs` directory:

- `client_messages.log`: Chat message history
- `mcp_client.log`: Client connection and operation logs
- `mcp_server.log`: Server operation logs

## Bank Information

The chatbot is configured with comprehensive bank information including:
- Business hours
- Branch locations
- Available services
- Contact information
- Support channels

## Development

### Adding New Features

1. Update the `BANK_INFO` dictionary in `app.py` for new bank information
2. Modify the `SYSTEM_MESSAGE` for updated AI behavior
3. Add new message handlers in `mcp_client.py` for additional functionality

### Testing

Run the test client to verify MCP functionality:
```bash
python test_client.py
```

Clear logs for testing:
```bash
python clear_logs.py
```

## Security

- API keys and sensitive information are stored in `.env`
- MCP provides secure message transmission
- Input validation and error handling are implemented

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact:
- Email: support@globaltrust.com
- Phone: 1-800-GTB-BANK 