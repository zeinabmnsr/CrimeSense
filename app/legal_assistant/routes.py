from flask import Blueprint, request, jsonify
from .rag_engine import generate_answer

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
