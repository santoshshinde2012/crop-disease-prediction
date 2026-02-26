"""FastAPI dependency injection functions."""
import logging

from fastapi import HTTPException, Request, status

from src.inference.predictor import DiseasePredictor

logger = logging.getLogger("api.dependencies")


def get_predictor(request: Request) -> DiseasePredictor:
    """Retrieve the DiseasePredictor instance loaded during app startup."""
    predictor = getattr(request.app.state, "predictor", None)
    if predictor is None:
        logger.error("Prediction requested but model is not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. The service is starting up or encountered an error.",
        )
    return predictor


async def validate_twilio_signature(request: Request) -> dict:
    """Validate the X-Twilio-Signature header and return parsed form data.

    When ``WHATSAPP_ENABLE_SIGNATURE_VALIDATION`` is ``False`` (e.g. local
    dev with ngrok), validation is skipped but the form data is still parsed
    and returned.
    """
    from twilio.request_validator import RequestValidator

    from api.config import (
        TWILIO_AUTH_TOKEN,
        TWILIO_WEBHOOK_URL,
        WHATSAPP_ENABLE_SIGNATURE_VALIDATION,
    )

    form = await request.form()
    params = {k: v for k, v in form.items()}

    if not WHATSAPP_ENABLE_SIGNATURE_VALIDATION:
        return params

    # Use the configured webhook URL if set (for proxied deployments),
    # otherwise reconstruct from the incoming request.
    url = TWILIO_WEBHOOK_URL or str(request.url)

    signature = request.headers.get("X-Twilio-Signature", "")
    validator = RequestValidator(TWILIO_AUTH_TOKEN)

    if not validator.validate(url, params, signature):
        logger.warning("Invalid Twilio signature from %s", request.client.host)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Twilio signature.",
        )

    return params
