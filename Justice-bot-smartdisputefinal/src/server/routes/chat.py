# routes/chat.py

from flask import Blueprint, request, jsonify, session
from services.case_builder import update_case_profile, generate_reply, recommend_form
from services.canlii_api import search_canlii
from services.canlii_search import get_relevant_cases  # Your curated mock case summaries

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    try:
        message = request.json.get("message", "").strip()
        if not message:
            return jsonify({"error": "Empty message"}), 400

        if "case_profile" not in session:
            session["case_profile"] = {}

        # Step 1: Update the user's structured CaseProfile
        session["case_profile"] = update_case_profile(session["case_profile"], message)

        # Step 2: Generate AI-style reply based on what info is still missing
        reply = generate_reply(session["case_profile"])

        # Step 3: Form recommendation (optional)
        form_data = None
        if recommend_form(session["case_profile"]):
            form_data = recommend_form(session["case_profile"])

        # Step 4: Get relevant CanLII cases — fallback to curated if API finds nothing
        canlii_cases = get_relevant_cases(session["case_profile"])

        if not canlii_cases:
            canlii_cases = search_canlii(
                query=session["case_profile"].get("issue", "legal issue"),
                jurisdiction=session["case_profile"].get("province", "on").lower(),
                document_type='decisions'
            )

        # Final response includes bot reply, form link, case law
        return jsonify({
            "reply": reply,
            "case_profile": session["case_profile"],
            "form_data": form_data,
            "cases": canlii_cases
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
