# WhatsApp Integration Guide

End-to-end setup for crop disease diagnosis via WhatsApp using Twilio.

Farmers send a leaf photo on WhatsApp and receive an instant diagnosis with disease name, confidence score, severity, treatment, and prevention tips — powered by the same MobileNetV2 model (97.8% accuracy, ~8 ms inference) that serves the Streamlit app and REST API.

---

## Architecture

```mermaid
architecture-beta
    service farmer(internet)[WhatsApp Farmer]
    service twilio(cloud)[Twilio API]
    group backend(server)[FastAPI Backend]
        service webhook(server)[WhatsApp Router] in backend
        service service(server)[WhatsApp Service] in backend
        service predictor(server)[DiseasePredictor] in backend
    service diseaseDb(database)[Disease Info]
    farmer:R --> L:twilio
    twilio:R --> L:webhook{group}
    webhook:R --> L:service
    service:R --> L:predictor
    predictor{group}:R --> L:diseaseDb
```

**Message flow:**

1. Farmer sends a leaf photo to the Twilio WhatsApp number
2. Twilio POSTs the webhook payload (form-encoded) to `POST /api/v1/whatsapp/webhook`
3. The endpoint validates the Twilio signature, downloads the image, and runs inference
4. A farmer-friendly diagnosis is returned as TwiML XML
5. Twilio delivers the reply to the farmer on WhatsApp

**Design decisions:**

- **Synchronous TwiML** — inference is ~8 ms, well within Twilio's 15-second timeout
- **Stateless** — each message is independent, no database or session store needed
- **Reuses existing predictor** — same `app.state.predictor` instance loaded at API startup

---

## Prerequisites

> Requires: `checkpoints/best_model.pth` and `outputs/metrics/class_names.json` from the Jupyter notebook (Step 2 of the [execution guide](execution-guide.md)).

| Requirement | Purpose |
|-------------|---------|
| Twilio account | [Sign up free](https://www.twilio.com/try-twilio) |
| Twilio WhatsApp Sandbox | Test number for development |
| ngrok | Tunnel local server to a public HTTPS URL |
| Python dependencies | `twilio>=9.0` and `httpx>=0.27` (already in `requirements.txt`) |

---

## Step 1 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs `twilio` (webhook signature validation) and `httpx` (async image download from Twilio media URLs) alongside all existing dependencies.

---

## Step 2 — Configure Twilio

### 2.1 Get Twilio Credentials

1. Go to [Twilio Console](https://console.twilio.com/)
2. Copy your **Account SID** and **Auth Token** from the dashboard

### 2.2 Activate WhatsApp Sandbox

1. Navigate to **Messaging → Try it out → Send a WhatsApp message**
2. Send the join code (e.g., `join <word>-<word>`) from your phone to the Twilio sandbox number (`+1 415 523 8886`)
3. Your phone is now connected to the sandbox

### 2.3 Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Disable signature validation for local dev with ngrok
WHATSAPP_ENABLE_SIGNATURE_VALIDATION=false
```

> **Security:** `.env` is already in `.gitignore`. Never commit Twilio credentials.

---

## Step 3 — Start the API Server

```bash
uvicorn api.main:app --reload --port 8000
```

Verify the model loaded:

```bash
curl http://localhost:8000/api/v1/health
```

Expected output:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_classes": 15
}
```

---

## Step 4 — Expose via ngrok

In a **separate terminal**:

```bash
ngrok http 8000
```

Copy the HTTPS forwarding URL (e.g., `https://abc123.ngrok-free.app`).

---

## Step 5 — Configure Twilio Webhook

1. Go to [Twilio Console → Sandbox Configuration](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Set **"When a message comes in"** to:

```
https://<your-ngrok-url>/api/v1/whatsapp/webhook
```

3. Set HTTP method to **POST**
4. Click **Save**

---

## Step 6 — Test on WhatsApp

Open WhatsApp and send messages to the Twilio sandbox number:

| Test | Send | Expected Response |
|------|------|-------------------|
| Greeting | `hi` | Welcome message with instructions |
| Help | `help` | Available commands and photo tips |
| Crop list | `crops` | Supported crops and diseases |
| Diagnosis | A leaf photo (JPEG/PNG) | Disease name, confidence, severity, treatment, prevention |
| Invalid media | A video or audio file | "I can only analyze leaf images" |

---

## Conversation Flow

```
┌────────────────────────────────────────────────────────────┐
│ WhatsApp Chat: CropDoc                                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ FARMER: hi                                                 │
│                                                            │
│ CROPDOC:                                                   │
│ 👋 Welcome to CropDoc!                                    │
│                                                            │
│ I can help identify diseases in your Corn, Potato,         │
│ and Tomato crops.                                          │
│                                                            │
│ 📸 Send me a photo of a diseased leaf, and I will         │
│ diagnose it with treatment recommendations.                │
│                                                            │
│ Type help for more options.                                │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ FARMER: [Sends photo of tomato leaf with brown spots]      │
│                                                            │
│ CROPDOC:                                                   │
│ 🌿 Crop Disease Analysis                                  │
│                                                            │
│ 🔬 Disease: Tomato: Early Blight                           │
│ 📊 Confidence: 95.2%                                      │
│ ⚠️ Severity: Moderate                                     │
│                                                            │
│ 💊 Treatment:                                              │
│ Apply chlorothalonil fungicide. Mulch around base to       │
│ prevent spore splash.                                      │
│                                                            │
│ 🛡️ Prevention:                                            │
│ • Stake plants for better air circulation                  │
│ • Apply mulch to prevent soil splash onto leaves           │
│ • Remove infected lower leaves promptly                    │
│                                                            │
│ 📸 Send another leaf photo for a new diagnosis.            │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ FARMER: [Sends healthy corn leaf photo]                    │
│                                                            │
│ CROPDOC:                                                   │
│ 🌿 Crop Disease Analysis                                  │
│                                                            │
│ ✅ Result: Corn: Healthy                                   │
│ 📊 Confidence: 98.7%                                      │
│                                                            │
│ Your plant looks healthy! Continue regular monitoring      │
│ and good agricultural practices.                           │
│                                                            │
│ 📸 Send another leaf photo anytime.                        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## API Endpoint Reference

### Webhook

```
POST /api/v1/whatsapp/webhook
Content-Type: application/x-www-form-urlencoded
```

Twilio sends these form fields:

| Field | Description |
|-------|-------------|
| `MessageSid` | Unique message ID |
| `From` | Sender's WhatsApp number (`whatsapp:+1234567890`) |
| `Body` | Text content of the message |
| `NumMedia` | Number of media attachments |
| `MediaUrl0` | URL of the first media attachment |
| `MediaContentType0` | MIME type (`image/jpeg`, `image/png`, etc.) |
| `ProfileName` | Sender's WhatsApp display name |

**Response:** TwiML XML with `Content-Type: text/xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>🌿 Crop Disease Analysis ...</Message>
</Response>
```

---

## File Structure

New and modified files for the WhatsApp integration:

```
api/
├── config.py                        # MODIFIED — Twilio env var loading
├── dependencies.py                  # MODIFIED — validate_twilio_signature()
├── main.py                          # MODIFIED — registered WhatsApp router
├── routers/
│   └── whatsapp.py                  # NEW — webhook endpoint
├── schemas/
│   └── whatsapp.py                  # NEW — Pydantic models + message templates
└── services/
    └── whatsapp_service.py          # NEW — image download, formatting, rate limiter

.env.example                         # NEW — documented environment variables
tests/
└── test_whatsapp.py                 # NEW — 29 unit tests
```

---

## Configuration Reference

All WhatsApp-specific settings are loaded from environment variables in `api/config.py`:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TWILIO_ACCOUNT_SID` | Yes | — | Twilio account SID (starts with `AC`) |
| `TWILIO_AUTH_TOKEN` | Yes | — | Twilio auth token |
| `TWILIO_WHATSAPP_NUMBER` | Yes | — | Twilio WhatsApp number (`whatsapp:+...`) |
| `TWILIO_WEBHOOK_URL` | No | — | Override URL for signature validation behind a proxy |
| `WHATSAPP_ENABLE_SIGNATURE_VALIDATION` | No | `true` | Set `false` for local dev with ngrok |
| `WHATSAPP_LOW_CONFIDENCE_THRESHOLD` | No | `0.60` | Below this confidence, show "low confidence" warning |
| `WHATSAPP_RATE_LIMIT_PER_MINUTE` | No | `10` | Max requests per phone number per minute |
| `WHATSAPP_IMAGE_DOWNLOAD_TIMEOUT` | No | `10` | Seconds to wait for Twilio media download |

---

## Security

| Measure | Implementation |
|---------|----------------|
| **Webhook authentication** | Every request validated via `X-Twilio-Signature` header using `twilio.request_validator.RequestValidator` |
| **Credential management** | `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` loaded from `.env` (gitignored) |
| **Rate limiting** | In-memory sliding window — 10 requests/min per phone number |
| **Image validation** | Max 10 MB, JPEG/PNG only, EXIF rotation handled |
| **Privacy** | Phone numbers logged as last 4 digits only |
| **XML injection** | All TwiML message content escaped via `xml.sax.saxutils.escape()` |

---

## Message Types & Responses

The webhook classifies incoming messages and responds accordingly:

| Message Type | Trigger | Response |
|-------------|---------|----------|
| **Greeting** | `hi`, `hello`, `hey`, `start` | Welcome message with instructions |
| **Help** | `help`, `?`, `menu` | Available commands and photo tips |
| **Crops** | `crops`, `diseases`, `list` | Supported crops and disease counts |
| **Image** | JPEG/PNG attachment | Full diagnosis with treatment |
| **Low confidence** | Image with prediction < 60% | Best guess + tips for better photos |
| **Non-image media** | Video, audio, document | "I can only analyze leaf images" |
| **Unknown text** | Any other text | Prompt to send a leaf photo |
| **Rate limited** | > 10 requests/min from same number | "Please wait a moment" |

---

## Running Tests

```bash
pytest tests/test_whatsapp.py -v
```

| Test Suite | Count | Coverage |
|-----------|-------|----------|
| Text commands (greeting, help, crops, unknown, case-insensitive) | 12 | Message routing |
| Non-image media (video, audio) | 2 | Error handling |
| Image prediction (success, healthy, low confidence, download failure) | 4 | End-to-end flow |
| Rate limiting (enforcement, per-number independence) | 2 | Abuse prevention |
| TwiML response (XML structure, escaping, raw XML) | 3 | Response format |
| Service unit tests (classify, format diseased/healthy/low-confidence) | 6 | Business logic |
| **Total** | **29** | |

---

## Production Deployment

Moving from the Twilio sandbox to production:

### 1. WhatsApp Business API

1. Apply for a [WhatsApp Business Account](https://www.twilio.com/whatsapp) via Twilio
2. Register and verify a dedicated phone number
3. Get your business profile approved by Meta

### 2. Server Requirements

- **HTTPS** — Twilio requires a valid TLS certificate (Let's Encrypt, etc.)
- **Stable URL** — Set `TWILIO_WEBHOOK_URL` to your production domain
- **Enable signature validation** — Set `WHATSAPP_ENABLE_SIGNATURE_VALIDATION=true`
- **Secrets** — Inject via deployment platform (Docker secrets, AWS Parameter Store, etc.)

### 3. Monitoring Checklist

| Check | How |
|-------|-----|
| Webhook reachable | `curl -X POST https://your-domain/api/v1/whatsapp/webhook` |
| Model loaded | `curl https://your-domain/api/v1/health` |
| Logs flowing | Check `api.whatsapp` logger output |
| Rate limiter active | Send 11+ messages in 1 minute from same number |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| ngrok URL changed after restart | Update the webhook URL in [Twilio Console sandbox settings](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn) |
| "Invalid Twilio signature" in dev | Set `WHATSAPP_ENABLE_SIGNATURE_VALIDATION=false` in `.env` |
| No response on WhatsApp | Check that ngrok is running and the FastAPI server shows the incoming POST in logs |
| "Model is not loaded" response | Ensure `checkpoints/best_model.pth` and `outputs/metrics/class_names.json` exist (run notebook first) |
| Image download timeout | Increase `WHATSAPP_IMAGE_DOWNLOAD_TIMEOUT` in `.env` or check network connectivity |
| "Could not process your image" | Ensure the photo is JPEG or PNG and under 10 MB |
| Rate limited unexpectedly | Increase `WHATSAPP_RATE_LIMIT_PER_MINUTE` or wait 60 seconds |
| Twilio sandbox expired | Re-send the join code from your phone to reactivate |
