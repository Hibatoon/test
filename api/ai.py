# api/ai.py
import os
import time

# We use google-genai SDK (Client picks up GEMINI_API_KEY or GOOGLE_API_KEY env var).
# Make sure to set GEMINI_API_KEY in Vercel (or set GOOGLE_API_KEY).
try:
    # modern SDK
    from google import genai
except Exception:
    genai = None

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
# default model; you can change to a specific available model
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # conservative default

def generate_reply(prompt: str, temperature: float = 0.2, max_output_tokens: int = 300, timeout_s: int = 8):
    """
    Generate a reply by calling Gemini via google-genai SDK.
    This function uses a short timeout and safe fallback.
    """
    # fallback
    fallback = "Sorry, I'm having trouble generating a reply right now."

    if genai is None:
        print("genai SDK not installed or import failed")
        return fallback

    # make sure API key exists — client will also pick up GEMINI_API_KEY env var
    if not GEMINI_API_KEY:
        print("No GEMINI_API_KEY found")
        return fallback

    # Create a client (the SDK reads env var, but explicitly constructing if supported)
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        try:
            client = genai.Client()
        except Exception as e:
            print("Could not create genai client:", e)
            return fallback

    # Build a small content payload
    try:
        # Use the SDK generate_content / models.generate_content pattern
        # different SDK versions vary — we try a common method
        start = time.time()
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens
            }
        )
        # Many SDK responses expose .text or .output
        if hasattr(resp, "text") and resp.text:
            return resp.text.strip()
        # try common dict shapes
        if isinstance(resp, dict):
            # check keys
            for key in ("output", "text", "content"):
                if key in resp:
                    return str(resp[key]).strip()
            # sometimes nested
            if "candidates" in resp and resp["candidates"]:
                return str(resp["candidates"][0].get("output", fallback)).strip()
    except Exception as e:
        print("Gemini generate error:", e)

    return fallback
