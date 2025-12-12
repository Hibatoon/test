from flask import Flask, request, jsonify
import os
import requests
import google.generativeai as genai

app = Flask(__name__)

MY_NUMBER = os.getenv("MY_NUMBER")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/", methods=["GET"])
def index():
    return {"status": "ok"}, 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge
        return "Invalid token", 403

    if request.method == "POST":
        data = request.json
        print("Received:", data)

        try:
            entry = data["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            messages = value.get("messages")

            if messages:
                message = messages[0]
                from_number = message["from"]
                text = message["text"]["body"]

                reply = generate_reply(text)
                send_whatsapp_message(from_number, reply)

        except Exception as e:
            print("Error parsing message:", e)

        return "OK", 200

def generate_reply(text):
    try:
        response = model.generate_content(f"Respond shortly to: {text}")
        return response.text
    except:
        return "Error generating reply."

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
    requests.post(url, headers=headers, json=payload)

@app.route("/daily", methods=["GET"])
def daily_message():
    try:
        send_whatsapp_message(MY_NUMBER, "Your daily automated message! 🌞")
        return {"status": "sent"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

handler = app
