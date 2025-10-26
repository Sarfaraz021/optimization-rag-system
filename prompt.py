# Create a LANGSMITH_API_KEY in Settings > API Keys
import os
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

client = Client(api_key=LANGSMITH_API_KEY)
rag_prompt = client.pull_prompt("rag-prompt")