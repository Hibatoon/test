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
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

def get_daily_news():
    url = (
        "https://newsapi.org/v2/top-headlines?"
        "language=en&"
        "pageSize=5&"  # Number of articles
        f"apiKey={NEWS_API_KEY}"
    )

    res = requests.get(url)
    data = res.json()

    if "articles" not in data:
        return "Couldn't fetch the news today."

    articles = data["articles"]

    news_message = "📰 *Today's Top News*\n\n"

    for i, article in enumerate(articles, start=1):
        title = article.get("title", "No title")
        source = article.get("source", {}).get("name", "Unknown")
        url = article.get("url", "")

        news_message += f"{i}. *{title}*\n   _({source})_\n"
        if url:
            news_message += f"   🔗 {url}\n\n"

    return news_message.strip()


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
        resp = model.generate_content(f"Reply concisely to: {text}")
        # safe extraction
        if hasattr(resp, "text") and resp.text:
            return resp.text
        if hasattr(resp, "response") and resp.response:
            return resp.response[0].content
        return "Sorry, couldn't generate a reply."
    except Exception as e:
        print("Gemini error:", e)
        return "Sorry, couldn't generate a reply."


def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"
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
    # news = get_daily_news()  # Fetch news from NewsAPI
    # send_whatsapp_message(MY_NUMBER, news)  # Send via WhatsApp
    send_whatsapp_message(MY_NUMBER, "news")  # Send via WhatsApp
    return {"status": "news_sent"}, 200


handler = app
