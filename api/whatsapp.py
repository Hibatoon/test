# api/whatsapp.py
import os
import requests
import json

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

def send_whatsapp_message(to: str, text: str):
    if not (WHATSAPP_TOKEN and PHONE_NUMBER_ID):
        print("Missing WHATSAPP_TOKEN or PHONE_NUMBER_ID")
        return None

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
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        print("WhatsApp API status:", r.status_code, r.text)
        return r
    except Exception as e:
        print("Error sending WhatsApp message:", e)
        return None
