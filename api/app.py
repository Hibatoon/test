# api/app.py
from flask import Flask, request, jsonify
import os
import threading
from ai import generate_reply
from whatsapp import send_whatsapp_message

app = Flask(__name__)

# envs (set these in Vercel dashboard)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
MY_NUMBER = os.getenv("MY_NUMBER")         # e.g. "2126xxxxxxxx"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

# quick health check
@app.route("/", methods=["GET"])
def root():
    return {"status": "ok"}, 200


# Webhook endpoint (Meta requires 200 quickly)
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Verification handshake
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge, 200
        return "Invalid token", 403

    # POST — incoming message
    data = request.json or {}
    print("Incoming webhook:", data)

    # parse message safely
    try:
        messages = (
            data.get("entry", [])[0]
            .get("changes", [])[0]
            .get("value", {})
            .get("messages", [])
        )
    except Exception as e:
        messages = []
        print("Parse error:", e)

    if not messages:
        # no message (e.g., status or other), return quickly
        return "OK", 200

    msg = messages[0]
    sender = msg.get("from")
    text = None
    if "text" in msg:
        text = msg["text"].get("body", "")

    # Basic quick replies for tiny rules — handle "hi" fast
    if text and text.strip().lower() == "hi":
        send_whatsapp_message(sender, "Hello! How can I help you today?")
        return "OK", 200

    # For AI replies, call Gemini (may take time). We must respond 200 quickly to Meta,
    # so spawn a background thread to call Gemini and send the reply.
    def process_and_reply(sender, text):
        try:
            # Build a prompt; include limited recent context if desired (stateless here)
            prompt = f"User: {text}\nAssistant:"
            ai_reply = generate_reply(prompt, temperature=0.5, max_output_tokens=256)
            if not ai_reply:
                ai_reply = "Sorry — I'm having trouble right now. Please try again later."
        except Exception as e:
            print("AI error:", e)
            ai_reply = "Sorry, I couldn't generate a reply right now."

        # send via WhatsApp Cloud API
        send_whatsapp_message(sender, ai_reply)

    threading.Thread(target=process_and_reply, args=(sender, text or "")).start()

    # Return to Meta quickly
    return "OK", 200


# Daily endpoint called by Vercel cron (or GitHub action)
@app.route("/daily", methods=["GET"])
def daily():
    if not (MY_NUMBER and WHATSAPP_TOKEN and PHONE_NUMBER_ID):
        return jsonify({"error": "Missing env variables for daily job"}), 500

    # create a daily prompt (you can expand templates)
    prompt = "Write a short friendly daily message (one sentence) with a tip and a quote."
    ai_reply = generate_reply(prompt, temperature=0.6, max_output_tokens=120)
    if not ai_reply:
        ai_reply = "Good morning! Have a great day :)"

    send_whatsapp_message(MY_NUMBER, ai_reply)
    return jsonify({"status": "sent"}), 200


# Required by Vercel
handler = app
