"""Tests for the WhatsApp Twilio integration."""
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch
from xml.etree import ElementTree

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.schemas.whatsapp import TwilioWebhookData

# ---------------------------------------------------------------------------
# We build a minimal FastAPI app that mirrors the real one but uses a mock
# predictor so we don't need the actual model weights at test time.
# ---------------------------------------------------------------------------

_DEFAULT_PREDICTION = {
    "top_class": "Tomato: Early Blight",
    "confidence": 0.952,
    "top_k_probs": {
        "Tomato: Early Blight": 0.952,
        "Tomato: Late Blight": 0.023,
        "Tomato: Septoria Leaf Spot": 0.010,
    },
    "recommendation": "Apply chlorothalonil fungicide.",
}

_mock_predictor_instance = MagicMock()
_mock_predictor_instance.num_classes = 15
_mock_predictor_instance.model_path = "mock_model.pth"
_mock_predictor_instance.predict.return_value = dict(_DEFAULT_PREDICTION)


def _build_test_app() -> FastAPI:
    """Create a FastAPI app with the WhatsApp router and a mock predictor."""
    from api.routers import whatsapp as whatsapp_module

    # Reset the module-level rate limiter so tests don't leak state
    whatsapp_module.rate_limiter = whatsapp_module.RateLimiter()

    app = FastAPI()
    app.state.predictor = _mock_predictor_instance
    app.include_router(whatsapp_module.router, prefix="/api/v1")
    return app


# Disable Twilio signature validation for all tests
@pytest.fixture(autouse=True)
def _disable_signature_validation():
    with patch("api.config.WHATSAPP_ENABLE_SIGNATURE_VALIDATION", False):
        yield


@pytest.fixture()
def client():
    # Restore default prediction before each test
    _mock_predictor_instance.predict.return_value = dict(_DEFAULT_PREDICTION)
    app = _build_test_app()
    return TestClient(app)


def _webhook_form(**overrides) -> dict:
    """Build a minimal Twilio webhook form payload."""
    defaults = {
        "MessageSid": "SM0001",
        "AccountSid": "AC0001",
        "From": "whatsapp:+1234567890",
        "To": "whatsapp:+14155238886",
        "Body": "",
        "NumMedia": "0",
    }
    defaults.update(overrides)
    return defaults


def _assert_valid_twiml(response) -> str:
    """Assert the response is valid TwiML XML and return the message body."""
    assert response.status_code == 200
    assert "text/xml" in response.headers.get("content-type", "")

    root = ElementTree.fromstring(response.text)
    assert root.tag == "Response"
    message_el = root.find("Message")
    assert message_el is not None
    return message_el.text or ""


def _create_minimal_jpeg() -> bytes:
    """Create a small valid JPEG image using PIL."""
    from PIL import Image

    buf = BytesIO()
    img = Image.new("RGB", (10, 10), color="green")
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _mock_httpx_download(jpeg_bytes: bytes):
    """Create a patched httpx.AsyncClient that returns the given bytes."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = jpeg_bytes
    mock_response.headers = {"content-type": "image/jpeg"}
    mock_response.raise_for_status = MagicMock()

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)
    mock_ctx.get = AsyncMock(return_value=mock_response)
    return mock_ctx


# ── Text command tests ────────────────────────────────────────


class TestTextCommands:
    """Verify that text-only messages route to the correct response."""

    @pytest.mark.parametrize("text", ["hi", "hello", "hey", "start"])
    def test_greeting(self, client, text):
        resp = client.post("/api/v1/whatsapp/webhook", data=_webhook_form(Body=text))
        body = _assert_valid_twiml(resp)
        assert "Welcome to CropDoc" in body

    @pytest.mark.parametrize("text", ["help", "?", "menu"])
    def test_help(self, client, text):
        resp = client.post("/api/v1/whatsapp/webhook", data=_webhook_form(Body=text))
        body = _assert_valid_twiml(resp)
        assert "Help" in body

    @pytest.mark.parametrize("text", ["crops", "diseases", "list"])
    def test_crops(self, client, text):
        resp = client.post("/api/v1/whatsapp/webhook", data=_webhook_form(Body=text))
        body = _assert_valid_twiml(resp)
        assert "Corn" in body
        assert "Potato" in body
        assert "Tomato" in body

    def test_unknown_text(self, client):
        resp = client.post(
            "/api/v1/whatsapp/webhook",
            data=_webhook_form(Body="random message"),
        )
        body = _assert_valid_twiml(resp)
        assert "photo" in body.lower()

    def test_case_insensitive(self, client):
        resp = client.post("/api/v1/whatsapp/webhook", data=_webhook_form(Body="HELP"))
        body = _assert_valid_twiml(resp)
        assert "Help" in body


# ── Non-image media tests ────────────────────────────────────


class TestNonImageMedia:
    """Messages with non-image attachments should get an error."""

    def test_video_attachment(self, client):
        resp = client.post(
            "/api/v1/whatsapp/webhook",
            data=_webhook_form(
                NumMedia="1",
                MediaUrl0="https://api.twilio.com/2010-04-01/video.mp4",
                MediaContentType0="video/mp4",
            ),
        )
        body = _assert_valid_twiml(resp)
        assert "only analyze" in body.lower()

    def test_audio_attachment(self, client):
        resp = client.post(
            "/api/v1/whatsapp/webhook",
            data=_webhook_form(
                NumMedia="1",
                MediaUrl0="https://api.twilio.com/2010-04-01/audio.ogg",
                MediaContentType0="audio/ogg",
            ),
        )
        body = _assert_valid_twiml(resp)
        assert "only analyze" in body.lower()


# ── Image prediction tests ───────────────────────────────────


class TestImagePrediction:
    """End-to-end image prediction flow with mocked HTTP download."""

    @patch("api.services.whatsapp_service.httpx.AsyncClient")
    def test_successful_prediction(self, mock_client_cls, client):
        mock_client_cls.return_value = _mock_httpx_download(_create_minimal_jpeg())

        resp = client.post(
            "/api/v1/whatsapp/webhook",
            data=_webhook_form(
                NumMedia="1",
                MediaUrl0="https://api.twilio.com/2010-04-01/media/img.jpg",
                MediaContentType0="image/jpeg",
            ),
        )
        body = _assert_valid_twiml(resp)
        assert "Tomato: Early Blight" in body
        assert "95.2%" in body
        assert "Treatment" in body

    @patch("api.services.whatsapp_service.httpx.AsyncClient")
    def test_healthy_prediction(self, mock_client_cls, client):
        _mock_predictor_instance.predict.return_value = {
            "top_class": "Tomato: Healthy",
            "confidence": 0.987,
            "top_k_probs": {"Tomato: Healthy": 0.987},
            "recommendation": "No disease detected.",
        }
        mock_client_cls.return_value = _mock_httpx_download(_create_minimal_jpeg())

        resp = client.post(
            "/api/v1/whatsapp/webhook",
            data=_webhook_form(
                NumMedia="1",
                MediaUrl0="https://api.twilio.com/2010-04-01/media/img.jpg",
                MediaContentType0="image/jpeg",
            ),
        )
        body = _assert_valid_twiml(resp)
        assert "Healthy" in body
        assert "healthy" in body.lower()

    @patch("api.services.whatsapp_service.httpx.AsyncClient")
    def test_low_confidence_prediction(self, mock_client_cls, client):
        _mock_predictor_instance.predict.return_value = {
            "top_class": "Corn: Common Rust",
            "confidence": 0.42,
            "top_k_probs": {"Corn: Common Rust": 0.42},
            "recommendation": "Apply fungicide.",
        }
        mock_client_cls.return_value = _mock_httpx_download(_create_minimal_jpeg())

        resp = client.post(
            "/api/v1/whatsapp/webhook",
            data=_webhook_form(
                NumMedia="1",
                MediaUrl0="https://api.twilio.com/2010-04-01/media/img.jpg",
                MediaContentType0="image/jpeg",
            ),
        )
        body = _assert_valid_twiml(resp)
        assert "Low Confidence" in body
        assert "42.0%" in body

    @patch("api.services.whatsapp_service.httpx.AsyncClient")
    def test_download_failure(self, mock_client_cls, client):
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_ctx.get = AsyncMock(side_effect=Exception("Connection refused"))
        mock_client_cls.return_value = mock_ctx

        resp = client.post(
            "/api/v1/whatsapp/webhook",
            data=_webhook_form(
                NumMedia="1",
                MediaUrl0="https://api.twilio.com/2010-04-01/media/img.jpg",
                MediaContentType0="image/jpeg",
            ),
        )
        body = _assert_valid_twiml(resp)
        assert "download" in body.lower() or "Could not" in body


# ── Rate limiting tests ───────────────────────────────────────


class TestRateLimiting:
    """Verify the per-phone-number rate limiter."""

    def test_rate_limit_enforcement(self):
        from api.services.whatsapp_service import RateLimiter

        limiter = RateLimiter(max_requests=3, window_seconds=60)
        phone = "whatsapp:+1111111111"

        assert limiter.is_allowed(phone) is True
        assert limiter.is_allowed(phone) is True
        assert limiter.is_allowed(phone) is True
        assert limiter.is_allowed(phone) is False  # 4th request blocked

    def test_different_numbers_independent(self):
        from api.services.whatsapp_service import RateLimiter

        limiter = RateLimiter(max_requests=1, window_seconds=60)

        assert limiter.is_allowed("whatsapp:+1111") is True
        assert limiter.is_allowed("whatsapp:+2222") is True
        assert limiter.is_allowed("whatsapp:+1111") is False
        assert limiter.is_allowed("whatsapp:+2222") is False


# ── TwiML response tests ─────────────────────────────────────


class TestTwiMLResponse:
    """All responses must be valid XML with correct content type."""

    def test_twiml_xml_structure(self):
        from api.services.whatsapp_service import WhatsAppService

        svc = WhatsAppService()
        resp = svc.create_twiml_response("Hello!")
        assert resp.media_type == "text/xml"

        root = ElementTree.fromstring(resp.body)
        assert root.tag == "Response"
        assert root.find("Message").text == "Hello!"

    def test_twiml_escapes_special_chars(self):
        from api.services.whatsapp_service import WhatsAppService

        svc = WhatsAppService()
        # This should not raise an XML parse error — the < and & are escaped
        resp = svc.create_twiml_response('Test <b>"quotes"</b> & ampersand')
        root = ElementTree.fromstring(resp.body)
        msg_text = root.find("Message").text
        # ElementTree unescapes XML entities, so we just verify round-trip
        assert '"quotes"' in msg_text
        assert "ampersand" in msg_text

    def test_twiml_raw_xml_is_escaped(self):
        from api.services.whatsapp_service import WhatsAppService

        svc = WhatsAppService()
        resp = svc.create_twiml_response("a < b & c > d")
        raw = resp.body.decode() if isinstance(resp.body, bytes) else resp.body
        assert "&lt;" in raw
        assert "&amp;" in raw
        assert "&gt;" in raw


# ── Service unit tests ────────────────────────────────────────


class TestWhatsAppService:
    """Unit tests for individual service methods."""

    def test_classify_greeting(self):
        from api.services.whatsapp_service import WhatsAppService

        data = TwilioWebhookData(
            MessageSid="SM1", AccountSid="AC1",
            From="whatsapp:+1", Body="hello", NumMedia=0,
        )
        assert WhatsAppService.classify_message(data) == "greeting"

    def test_classify_image(self):
        from api.services.whatsapp_service import WhatsAppService

        data = TwilioWebhookData(
            MessageSid="SM1", AccountSid="AC1",
            From="whatsapp:+1", Body="", NumMedia=1,
            MediaUrl0="https://example.com/img.jpg",
            MediaContentType0="image/jpeg",
        )
        assert WhatsAppService.classify_message(data) == "image"

    def test_classify_non_image_media(self):
        from api.services.whatsapp_service import WhatsAppService

        data = TwilioWebhookData(
            MessageSid="SM1", AccountSid="AC1",
            From="whatsapp:+1", Body="", NumMedia=1,
            MediaUrl0="https://example.com/v.mp4",
            MediaContentType0="video/mp4",
        )
        assert WhatsAppService.classify_message(data) == "non_image_media"

    def test_format_diseased_response(self):
        from api.services.whatsapp_service import WhatsAppService

        result = {
            "top_class": "Tomato: Early Blight",
            "confidence": 0.95,
            "recommendation": "Apply fungicide.",
        }
        details = {
            "crop": "Tomato",
            "severity": "Moderate",
            "treatment": "Apply chlorothalonil.",
            "prevention": ["Stake plants", "Mulch"],
        }
        msg = WhatsAppService.format_prediction_response(result, details, 0.60)
        assert "Early Blight" in msg
        assert "95.0%" in msg
        assert "Moderate" in msg
        assert "Stake plants" in msg
        assert len(msg) < 1600

    def test_format_healthy_response(self):
        from api.services.whatsapp_service import WhatsAppService

        result = {"top_class": "Corn: Healthy", "confidence": 0.99}
        details = {"crop": "Corn", "severity": "None"}
        msg = WhatsAppService.format_prediction_response(result, details, 0.60)
        assert "Healthy" in msg
        assert "healthy" in msg.lower()
        assert len(msg) < 1600

    def test_format_low_confidence_response(self):
        from api.services.whatsapp_service import WhatsAppService

        result = {"top_class": "Corn: Common Rust", "confidence": 0.35}
        details = {"crop": "Corn", "severity": "Moderate"}
        msg = WhatsAppService.format_prediction_response(result, details, 0.60)
        assert "Low Confidence" in msg
        assert "35.0%" in msg
        assert len(msg) < 1600
