from .vector_store import search
import requests
import os
from dotenv import load_dotenv 

load_dotenv()
# Load API key (failsafe fallback)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_answer(query):
    context_chunks = search(query, top_k=1)
    context = "\n".join(context_chunks) if context_chunks else "No relevant context available."

    system_prompt = (
        "You are a UK legal assistant. Use the given context to help answer legal questions clearly, concisely, and truthfully."
    )

    user_prompt = f"""Context:\n{context}\n\nUser question: {query}"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",  # change to your domain in prod
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        print("🔁 Raw text from OpenRouter:", response.text)
        response.raise_for_status()
        res_json = response.json()

        print("🧠 OpenRouter raw response:", res_json)  # Debug log

        if "choices" not in res_json or not res_json["choices"]:
            return "⚠️ OpenRouter didn't return a valid response."
        
        return res_json["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        print("❌ Request to OpenRouter failed:", e)
        return "❌ Failed to contact the legal assistant service."

    except Exception as e:
        print("❌ Unexpected error:", e)
        return "⚠️ An unexpected error occurred while generating the response."
