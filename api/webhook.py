from flask import Flask, request
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# @app.route("/", methods=["GET", "POST"])
@app.route("/api/webhook", methods=["GET", "POST"])

def webhook():
    # Verification (Meta Webhook setup)
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge
        return "Invalid token", 403

    # Handle incoming messages
    if request.method == "POST":
        data = request.json
        print("Received:", data)

        # Example: parse WhatsApp message
        try:
            entry = data["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            messages = value.get("messages")
            if messages:
                message = messages[0]
                from_number = message["from"]
                text = message["text"]["body"]

                # Decide response based on message text
                if text.lower() == "hi":
                    reply = "Hello! How can I help you today?"
                else:
                    reply = "Sorry, I only understand 'hi' for now."

                # Send response back via WhatsApp API
                send_whatsapp_message(from_number, reply)
        except Exception as e:
            print("Error parsing message:", e)

        return "OK", 200

def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v16.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("WhatsApp API response:", response.status_code, response.text)
