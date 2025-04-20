import os  
from openai import AzureOpenAI  
from dotenv import load_dotenv

load_dotenv()
        
# Initialize client
client = AzureOpenAI(
    azure_endpoint=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2023-12-01-preview"
)
deployment = os.getenv("DEPLOYMENT_NAME")

# Prepare the messages for chat completion
messages = [
    {
        "role": "user",
        "content": "Write a short hello world message"
    }
]

# Generate the completion
try:
    completion = client.chat.completions.create(
        model=deployment,
        messages=messages,
        max_tokens=100,
        temperature=0.5,
        top_p=0.9,
        frequency_penalty=0,
        presence_penalty=0
    )
    # Print the response
    print(completion.choices[0].message.content)
except Exception as e:
    print(f"An error occurred: {str(e)}")
    