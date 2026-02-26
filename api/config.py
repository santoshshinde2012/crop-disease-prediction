"""API-specific configuration constants."""
import os
from pathlib import Path

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

# ── General ───────────────────────────────────────────────────
API_VERSION: str = "1.0.0"
MAX_FILE_SIZE_MB: int = 10
ALLOWED_CONTENT_TYPES: set[str] = {"image/jpeg", "image/png"}

# ── CORS ──────────────────────────────────────────────────────
# Comma-separated origins, or "*" for development
CORS_ORIGINS: list[str] = [
    o.strip()
    for o in os.environ.get("CORS_ORIGINS", "*").split(",")
    if o.strip()
]

# ── Rate limiting ─────────────────────────────────────────────
PREDICT_RATE_LIMIT_PER_MINUTE: int = int(
    os.environ.get("PREDICT_RATE_LIMIT_PER_MINUTE", "30")
)

# ── Twilio WhatsApp configuration ─────────────────────────────
TWILIO_ACCOUNT_SID: str = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN: str = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER: str = os.environ.get("TWILIO_WHATSAPP_NUMBER", "")
TWILIO_WEBHOOK_URL: str | None = os.environ.get("TWILIO_WEBHOOK_URL")

WHATSAPP_LOW_CONFIDENCE_THRESHOLD: float = float(
    os.environ.get("WHATSAPP_LOW_CONFIDENCE_THRESHOLD", "0.60")
)
WHATSAPP_RATE_LIMIT_PER_MINUTE: int = int(
    os.environ.get("WHATSAPP_RATE_LIMIT_PER_MINUTE", "10")
)
WHATSAPP_ENABLE_SIGNATURE_VALIDATION: bool = (
    os.environ.get("WHATSAPP_ENABLE_SIGNATURE_VALIDATION", "true").lower() == "true"
)
WHATSAPP_IMAGE_DOWNLOAD_TIMEOUT: int = int(
    os.environ.get("WHATSAPP_IMAGE_DOWNLOAD_TIMEOUT", "10")
)
