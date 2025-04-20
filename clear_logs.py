import os

def clear_logs():
    log_dir = 'logs'
    log_files = ['client_messages.log', 'mcp_client.log']
    
    for log_file in log_files:
        file_path = os.path.join(log_dir, log_file)
        try:
            open(file_path, 'w').close()
            print(f"Cleared {log_file}")
        except Exception as e:
            print(f"Error clearing {log_file}: {e}")

if __name__ == "__main__":
    clear_logs() 