import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")


client = genai.Client(
    api_key=GEMINI_API_KEY
)


print("Testing Gemini API...")

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say exactly: Gemini is working!"
)

print("Gemini response:")
print(response.text)