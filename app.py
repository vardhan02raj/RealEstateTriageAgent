"""
Real Estate Triage Agent - Web Application
"""

import os

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, render_template, request
from google import genai

from agent_logic import process_message

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Configure Google AI
api_key = os.environ.get("GOOGLE_API_KEY")
welcome_message = "Welcome to the Real Estate Triage Agent!"
if api_key:
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Write one short, friendly sentence welcoming someone to a real estate assistant. Be warm and professional. No quotes."
        )
        welcome_message = response.text.strip()
    except Exception:
        pass
else:
    print("Warning: GOOGLE_API_KEY not set. Welcome message will use default text.")


@app.route("/")
def index():
    """Serve the main UI."""
    return render_template("index.html", welcome_message=welcome_message)


@app.route("/api/chat", methods=["POST"])
def chat():
    """Process a chat message and return the agent's response."""
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing message"}), 400

    message = data["message"]
    state = data.get("state", {})

    reply, new_state, done = process_message(message, state)

    return jsonify({
        "reply": reply,
        "state": new_state,
        "done": done,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
