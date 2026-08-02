import os
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

API_URL = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Say 'connection successful' and nothing else."}]
}

response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
print(f"Status code: {response.status_code}")
print(f"Response: {response.text[:500]}")