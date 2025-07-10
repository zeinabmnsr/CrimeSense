from .vector_store import search
import requests
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_answer(query):
    context = "\n".join(search(query, top_k=1))

    prompt = f"""You are a UK legal assistant. Use the context below to answer the user's legal question briefly and clearly.

Context:
{context}
User question: {query}
Answer:"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://yourdomain.com",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"].strip()