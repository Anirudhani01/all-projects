import os
import subprocess
from dotenv import load_dotenv
import requests  # Add this import

# --- LLM Clients ---
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Load environment variables
load_dotenv()

# --- Conditional Initialization ---
openai_client = None
if os.getenv("OPENAI_API_KEY") and OpenAI:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

gemini_enabled = False
if os.getenv("GOOGLE_API_KEY") and genai:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini_enabled = True

# --- Prompt Template ---
ANALYSER_PROMPT = """
You are a User Story Analyzer.
Your task:
- Read the user story carefully.
- Identify what the user *wants to achieve* (the intent).
- Summarize the main goal in 2–3 sentences.
- Extract key requirements (functional needs).

User Story: {user_story}
"""

# --- Helper Functions ---
def call_openai(prompt: str) -> str:
    """Call OpenAI GPT model."""
    print("⚡ Using OpenAI GPT...")
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You analyze user stories and explain what the user wants."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ OpenAI call failed: {e}")
        return ""

def call_gemini(prompt: str) -> str:
    """Call Google Gemini model."""
    if not gemini_enabled:
        return ""
    print("⚡ Using Google Gemini...")
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Gemini call failed: {e}")
        return ""

def call_local_ollama(prompt: str, model: str = "openai/gpt-oss-20b") -> str:
    """Call Local Ollama Server via HTTP API."""
    print(f"⚡ Using Local Ollama Server ({model})...")
    try:
        # Prepare the request payload
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You analyze user stories and explain what the user wants."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4000,
            "stream": False
        }
        
        # Make the HTTP request to your local Ollama server
        response = requests.post(
            "http://192.168.0.155:1234/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            output_text = result["choices"][0]["message"]["content"]
            print(f"📝 Local Ollama response length: {len(output_text)} characters")
            return output_text
        else:
            print(f"❌ Local Ollama server error: {response.status_code} - {response.text}")
            return ""
            
    except requests.exceptions.Timeout:
        print("❌ Local Ollama server request timed out (5 minutes)")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"❌ Local Ollama server connection failed: {e}")
        return ""
    except Exception as e:
        print(f"❌ Local Ollama call failed: {e}")
        return ""

# --- Main Analyzer Function ---
def analyse_user_story(user_story: str) -> str:
    """Analyse user story with fallback logic."""
    prompt = ANALYSER_PROMPT.format(user_story=user_story)

    if openai_client:
        response = call_openai(prompt)
        if response:
            return response

    if gemini_enabled:
        response = call_gemini(prompt)
        if response:
            return response

    return call_local_ollama(prompt)

# --- Example Usage ---
if __name__ == "__main__":
    story = input("Enter your user story: ")
    print("\n⏳ Analysing user story...\n")
    analysis = analyse_user_story(story)
    print("\n✅ User Story Analysis:\n")
    print(analysis)
