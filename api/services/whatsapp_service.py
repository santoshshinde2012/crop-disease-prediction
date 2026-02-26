"""WhatsApp business logic — image download, response formatting, rate limiting."""
import logging
import time
from collections import defaultdict
from io import BytesIO
from xml.sax.saxutils import escape

import httpx
from fastapi import Response
from PIL import Image, ImageOps

from api.config import (
    ALLOWED_CONTENT_TYPES,
    MAX_FILE_SIZE_MB,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    WHATSAPP_IMAGE_DOWNLOAD_TIMEOUT,
    WHATSAPP_RATE_LIMIT_PER_MINUTE,
)
from api.schemas.whatsapp import TwilioWebhookData

logger = logging.getLogger("api.whatsapp")

# Text commands mapped to message types
_GREETING_KEYWORDS = {"hi", "hello", "hey", "start"}
_HELP_KEYWORDS = {"help", "?", "menu"}
_CROPS_KEYWORDS = {"crops", "diseases", "list"}


class RateLimiter:
    """In-memory sliding-window rate limiter keyed by phone number."""

    def __init__(self, max_requests: int | None = None, window_seconds: int = 60):
        self.max_requests = max_requests or WHATSAPP_RATE_LIMIT_PER_MINUTE
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, phone_number: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds

        # Prune expired timestamps
        self._requests[phone_number] = [
            t for t in self._requests[phone_number] if t > cutoff
        ]

        if len(self._requests[phone_number]) >= self.max_requests:
            return False

        self._requests[phone_number].append(now)
        return True


class WhatsAppService:
    """Handles image downloading, message classification, and response formatting."""

    # ── Message classification ────────────────────────────────

    @staticmethod
    def classify_message(data: TwilioWebhookData) -> str:
        """Classify an incoming WhatsApp message by type.

        Returns one of: "greeting", "help", "crops", "image",
        "non_image_media", "unknown".
        """
        has_media = data.num_media > 0

        if has_media:
            content_type = (data.media_content_type_0 or "").lower()
            if content_type.startswith("image/"):
                return "image"
            return "non_image_media"

        text = data.body.strip().lower()
        if text in _GREETING_KEYWORDS:
            return "greeting"
        if text in _HELP_KEYWORDS:
            return "help"
        if text in _CROPS_KEYWORDS:
            return "crops"
        return "unknown"

    # ── Image downloading ─────────────────────────────────────

    @staticmethod
    async def download_image(media_url: str) -> Image.Image:
        """Download an image from a Twilio media URL and return a PIL Image.

        Uses HTTP Basic Auth with Twilio credentials. Validates file size
        and format. Applies EXIF transpose for phone-taken photos.
        """
        max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024

        async with httpx.AsyncClient(
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=WHATSAPP_IMAGE_DOWNLOAD_TIMEOUT,
            follow_redirects=True,
        ) as client:
            response = await client.get(media_url)
            response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        if not content_type.startswith("image/"):
            raise ValueError(f"Unexpected content type: {content_type}")

        image_bytes = response.content
        if len(image_bytes) > max_bytes:
            raise ValueError(
                f"Image too large ({len(image_bytes) / (1024 * 1024):.1f} MB)"
            )

        image = Image.open(BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image)
        return image.convert("RGB")

    # ── Response formatting ───────────────────────────────────

    @staticmethod
    def format_prediction_response(
        result: dict,
        disease_details: dict,
        low_confidence_threshold: float,
    ) -> str:
        """Format a model prediction into a farmer-friendly WhatsApp message."""
        disease_name = result["top_class"]
        confidence = result["confidence"]
        confidence_pct = f"{confidence * 100:.1f}%"

        # Low confidence — ask for a better photo
        if confidence < low_confidence_threshold:
            return (
                "\U0001f33f *Crop Disease Analysis*\n"
                "\n"
                "\u26a0\ufe0f *Low Confidence Result*\n"
                f"Our best guess is *{disease_name}* ({confidence_pct}), "
                "but we are not certain.\n"
                "\n"
                "\U0001f4a1 *Tips for a better photo:*\n"
                "\u2022 Use good lighting (natural daylight is best)\n"
                "\u2022 Focus on a single leaf showing symptoms\n"
                "\u2022 Avoid blurry or distant shots\n"
                "\n"
                "Please try again or consult a local agronomist."
            )

        severity = disease_details.get("severity", "Unknown")
        is_healthy = severity == "None"

        # Healthy plant
        if is_healthy:
            return (
                "\U0001f33f *Crop Disease Analysis*\n"
                "\n"
                f"\u2705 *Result:* {disease_name}\n"
                f"\U0001f4ca *Confidence:* {confidence_pct}\n"
                "\n"
                "Your plant looks healthy! Continue regular monitoring "
                "and good agricultural practices.\n"
                "\n"
                "\U0001f4f8 Send another leaf photo anytime."
            )

        # Diseased plant — full diagnosis
        treatment = disease_details.get(
            "treatment", result.get("recommendation", "Consult a local agronomist.")
        )
        prevention = disease_details.get("prevention", [])

        lines = [
            "\U0001f33f *Crop Disease Analysis*",
            "",
            f"\U0001f52c *Disease:* {disease_name}",
            f"\U0001f4ca *Confidence:* {confidence_pct}",
            f"\u26a0\ufe0f *Severity:* {severity}",
            "",
            f"\U0001f48a *Treatment:*\n{treatment}",
        ]

        if prevention:
            lines.append("")
            lines.append("\U0001f6e1\ufe0f *Prevention:*")
            for tip in prevention:
                lines.append(f"\u2022 {tip}")

        lines.append("")
        lines.append("\U0001f4f8 Send another leaf photo for a new diagnosis.")

        return "\n".join(lines)

    # ── TwiML helper ──────────────────────────────────────────

    @staticmethod
    def create_twiml_response(message: str) -> Response:
        """Wrap a text message in TwiML XML and return a FastAPI Response."""
        escaped = escape(message)
        twiml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<Response>"
            f"<Message>{escaped}</Message>"
            "</Response>"
        )
        return Response(content=twiml, media_type="text/xml")
