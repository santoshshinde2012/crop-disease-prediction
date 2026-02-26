"""WhatsApp webhook — receives messages via Twilio, returns TwiML responses."""
import logging
import time

from fastapi import APIRouter, Depends, Response

from api.config import WHATSAPP_LOW_CONFIDENCE_THRESHOLD
from api.dependencies import get_predictor, validate_twilio_signature
from api.schemas.whatsapp import (
    ERROR_DOWNLOAD_MSG,
    ERROR_GENERIC_MSG,
    ERROR_INVALID_IMAGE_MSG,
    ERROR_NON_IMAGE_MSG,
    ERROR_RATE_LIMITED_MSG,
    GREETING_MSG,
    HELP_MSG,
    PROMPT_SEND_PHOTO_MSG,
    SUPPORTED_CROPS_MSG,
    TwilioWebhookData,
)
from api.services.whatsapp_service import RateLimiter, WhatsAppService
from src.data.disease_info import DISEASE_DETAILS
from src.inference.predictor import DiseasePredictor

logger = logging.getLogger("api.whatsapp")

router = APIRouter(tags=["WhatsApp"])

rate_limiter = RateLimiter()
service = WhatsAppService()


@router.post(
    "/whatsapp/webhook",
    summary="Twilio WhatsApp webhook",
    description="Receives WhatsApp messages via Twilio and responds with crop disease analysis.",
    response_class=Response,
    include_in_schema=False,
)
async def whatsapp_webhook(
    form_data: dict = Depends(validate_twilio_signature),
    predictor: DiseasePredictor = Depends(get_predictor),
):
    try:
        webhook = TwilioWebhookData(**form_data)

        # Rate limiting per phone number
        if not rate_limiter.is_allowed(webhook.from_number):
            logger.warning(
                "Rate limited: ...%s", webhook.from_number[-4:]
            )
            return service.create_twiml_response(ERROR_RATE_LIMITED_MSG)

        msg_type = service.classify_message(webhook)

        # ── Text commands ─────────────────────────────────────
        if msg_type == "greeting":
            return service.create_twiml_response(GREETING_MSG)
        if msg_type == "help":
            return service.create_twiml_response(HELP_MSG)
        if msg_type == "crops":
            return service.create_twiml_response(SUPPORTED_CROPS_MSG)
        if msg_type == "non_image_media":
            return service.create_twiml_response(ERROR_NON_IMAGE_MSG)
        if msg_type == "unknown":
            return service.create_twiml_response(PROMPT_SEND_PHOTO_MSG)

        # ── Image prediction flow ─────────────────────────────
        # Download image from Twilio
        try:
            image = await service.download_image(webhook.media_url_0)
        except Exception:
            logger.error("Image download failed for ...%s", webhook.from_number[-4:], exc_info=True)
            return service.create_twiml_response(ERROR_DOWNLOAD_MSG)

        # Run prediction
        try:
            start = time.perf_counter()
            result = predictor.predict(image, top_k=3)
            inference_ms = (time.perf_counter() - start) * 1000
        except Exception:
            logger.error("Inference failed for ...%s", webhook.from_number[-4:], exc_info=True)
            return service.create_twiml_response(ERROR_INVALID_IMAGE_MSG)

        disease_name = result["top_class"]
        details = DISEASE_DETAILS.get(disease_name, {})

        logger.info(
            "WhatsApp prediction: %s (%.1f%%) in %.0f ms for ...%s",
            disease_name,
            result["confidence"] * 100,
            inference_ms,
            webhook.from_number[-4:],
        )

        response_text = service.format_prediction_response(
            result, details, WHATSAPP_LOW_CONFIDENCE_THRESHOLD
        )
        return service.create_twiml_response(response_text)

    except Exception:
        logger.error("WhatsApp webhook error", exc_info=True)
        return service.create_twiml_response(ERROR_GENERIC_MSG)
