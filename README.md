# WhatsApp AI Agent (Flask + Vercel + Gemini)

## Setup
1. Push this repo to GitHub.
2. On Vercel, import the repo and set environment variables:
   - VERIFY_TOKEN
   - WHATSAPP_TOKEN
   - PHONE_NUMBER_ID
   - MY_NUMBER
   - GEMINI_API_KEY  (or GOOGLE_API_KEY)
   - (optional) GEMINI_MODEL

3. Deploy to Vercel.

## Endpoints
- `GET /api/` — health
- `POST /api/webhook` — WhatsApp webhook (configure in Meta)
- `GET /api/daily` — daily message (triggered by Vercel cron or GitHub Actions)

## Notes
- Vercel serverless functions have short lifetimes — Gemini calls must be reasonably fast.
- For production, use a persistent DB (Redis/Firestore) to store conversation state and rate limits.
