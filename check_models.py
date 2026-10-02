import os
from dotenv import load_dotenv
from google import genai

# Load configuration
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Lists all available models to verify if newer versions like Gemini 3 are active
print("--- FETCHING PROJECT MODELS ---")
try:
    for model in client.models.list():
        print(f"✅ Available: {model.name}")
except Exception as e:
    print(f"❌ API Error: {e}")