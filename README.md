# WhatsApp AI News Agent

A WhatsApp bot that delivers personalized news summaries powered by AI. Built with Flask, deployed on Vercel, and integrated with WhatsApp Business API.

## Features

- 🤖 **AI-Powered Summaries**: Uses Google Gemini to create concise, professional news summaries
- 📰 **Real-Time News**: Fetches latest headlines from NewsAPI across multiple categories
- ⏰ **Daily Digest**: Automated daily news delivery at 20:00 via Vercel Cron
- 💬 **Interactive Chat**: Responds to user commands for specific news categories
- 🔄 **WhatsApp Integration**: Full webhook integration with Meta's WhatsApp Business API

## Tech Stack

- **Backend**: Flask (Python)
- **Deployment**: Vercel Serverless Functions
- **AI**: Google Gemini API
- **News Source**: NewsAPI
- **Messaging**: WhatsApp Business Cloud API

## Project Structure

```
whatsapp_agent/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── vercel.json        # Vercel deployment configuration
└── README.md          # Project documentation
```

## Setup

### Prerequisites

- Python 3.9+
- Vercel account
- WhatsApp Business API account
- NewsAPI key
- Google Gemini API key

### Environment Variables

Configure these variables in your Vercel project settings:

```env
WHATSAPP_TOKEN=your_whatsapp_access_token
VERIFY_TOKEN=your_webhook_verify_token
PHONE_NUMBER_ID=your_whatsapp_phone_number_id
NEWS_API_KEY=your_newsapi_key
GEMINI_API_KEY=your_gemini_api_key
MY_NUMBER=your_whatsapp_number_with_country_code
```

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/Hibatoon/test.git
cd whatsapp_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Deployment

Deploy to Vercel:
```bash
vercel --prod
```

## API Endpoints

### `GET /webhook`
WhatsApp webhook verification endpoint. Meta uses this to verify your webhook URL.

**Parameters:**
- `hub.mode`: Should be "subscribe"
- `hub.verify_token`: Your verification token
- `hub.challenge`: Challenge string to return

### `POST /webhook`
Receives incoming WhatsApp messages and processes user commands.

### `GET/POST /send_daily_news`
Triggers the daily news digest. Called automatically by Vercel Cron at 20:00 UTC.

### `GET /health`
Health check endpoint to verify service status.

### `GET /`
Home endpoint with API information.

## Usage

### User Commands

Send these messages to your WhatsApp bot:

- **`hi`** or **`hello`** - Get welcome message and help
- **`news`** - Get general top headlines
- **`news tech`** - Get technology news
- **`news business`** - Get business/economy news
- **`news sports`** - Get sports news
- **`news health`** - Get health news
- **`news science`** - Get science news
- **`news entertainment`** - Get entertainment news
- **`news world`** - Get international news
- **`help`** - Display available commands

### Daily News

The bot automatically sends a curated news digest to the configured `MY_NUMBER` at 20:00 UTC daily.

## How It Works

1. **Message Reception**: WhatsApp forwards user messages to the `/webhook` endpoint
2. **Command Processing**: The bot parses the message and identifies the requested news category
3. **News Fetching**: Retrieves latest articles from NewsAPI based on the category
4. **AI Summarization**: Google Gemini generates professional, concise summaries
5. **Response Delivery**: Formatted message is sent back via WhatsApp Business API
6. **Scheduled Digest**: Vercel Cron triggers daily news delivery automatically

## Configuration

### Vercel Cron

The daily news is scheduled in `vercel.json`:
```json
"crons": [
  {
    "path": "/send_daily_news",
    "schedule": "0 20 * * *"
  }
]
```

### WhatsApp Webhook Setup

1. Go to your Meta App Dashboard
2. Configure webhook URL: `https://your-app.vercel.app/webhook`
3. Set verify token to match your `VERIFY_TOKEN`
4. Subscribe to `messages` webhook field

## Dependencies

```
Flask==3.0.0
requests==2.31.0
python-dotenv==1.0.0
Werkzeug==3.0.1
```

## Features in Detail

### AI Summarization
- Uses Google Gemini Pro model
- Generates 5-8 bullet points per news digest
- Professional journalistic tone
- Includes relevant emojis and source attribution
- Fallback to basic formatting if API fails

### Error Handling
- Comprehensive error logging
- Graceful degradation when services are unavailable
- Request timeouts to prevent hanging
- HTTP status code validation

### News Categories
Supports 7 news categories:
- General/World
- Technology
- Business
- Sports
- Health
- Science
- Entertainment

## Troubleshooting

### Webhook Verification Fails
- Ensure `VERIFY_TOKEN` matches in both Vercel and Meta settings
- Check that webhook URL is accessible
- Verify the URL ends with `/webhook`

### Messages Not Sending
- Confirm `WHATSAPP_TOKEN` is valid and not expired
- Verify `PHONE_NUMBER_ID` is correct
- Ensure recipient number is registered as a test user
- Check Vercel logs for detailed error messages

### Daily News Not Arriving
- Verify Vercel Cron is enabled for your project
- Check `MY_NUMBER` is set correctly with country code
- Review Vercel Function logs for execution details

## Repository

[GitHub Repository](https://github.com/Hibatoon/test)
