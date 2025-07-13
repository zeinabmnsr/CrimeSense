from flask import Blueprint, request, jsonify
from .rag_engine import generate_answer
from flask import render_template

legal_bp = Blueprint("legal", __name__, url_prefix="/api/legalbot")

@legal_bp.route("", methods=["POST"])
def legal_chat():
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "No query provided."}), 400

    try:
        answer = generate_answer(query)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@legal_bp.route("/chat-ui")
def legal_chat_ui():
    return render_template("legal_chatbot.html")

#"RAG" system working:
# User query → vector → similar legal text
#  → send to model → generate reply
'''
Now You Can Test the Chatbot!
Use Postman/Thunder Client:
POST /api/legalbot
Body (JSON):
json
Copy code
{
  "query": "Can I be arrested for trespassing?"
}
✅ If it returns a legal-sounding answer, 
you’re done with Phase 1 🎉

'''