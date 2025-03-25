import os
import requests
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv  # Load environment variables

# Load .env file
load_dotenv()

# Get API Key from environment variables
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("Missing API Key! Set it in the .env file.")

API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={API_KEY}"

app = Flask(__name__)

# Allow CORS for all origins (for development purposes)
CORS(app)  # Change this to restrict origins in production

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_response(user_input):
    """ Sends user input to Gemini AI API and returns the response. """
    payload = {"contents": [{"parts": [{"text": user_input}]}]}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Extract AI response safely
        candidates = data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "🤖 Gemini AI: No valid response received.")
        
        logging.warning("AI response structure unexpected: %s", data)
        return "🤖 Gemini AI: No valid response received."

    except requests.exceptions.RequestException as e:
        logging.error("API Request Error: %s", e)
        return "❌ API Error: Unable to process request."

@app.route("/chat", methods=["POST"])
def chat():
    """ API endpoint for chatbot interaction. """
    try:
        data = request.get_json()
        logging.info("Received data: %s", data)  # Log the received data
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"response": "❌ Error: Empty message received"}), 400

        response_text = get_response(user_input)
        return jsonify({"response": response_text})

    except Exception as e:
        logging.error("Unexpected Error: %s", e)
        return jsonify({"response": "❌ Server Error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)