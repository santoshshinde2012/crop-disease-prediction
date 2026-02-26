"""WhatsApp webhook schemas and response message templates."""
from pydantic import BaseModel, Field


class TwilioWebhookData(BaseModel):
    """Parsed Twilio webhook form data."""

    message_sid: str = Field(..., alias="MessageSid")
    account_sid: str = Field(..., alias="AccountSid")
    from_number: str = Field(..., alias="From")
    to_number: str = Field("", alias="To")
    body: str = Field("", alias="Body")
    num_media: int = Field(0, alias="NumMedia")
    media_url_0: str | None = Field(None, alias="MediaUrl0")
    media_content_type_0: str | None = Field(None, alias="MediaContentType0")
    profile_name: str | None = Field(None, alias="ProfileName")

    model_config = {"populate_by_name": True}


# ── WhatsApp message templates ────────────────────────────────
# All templates stay under WhatsApp's 1600 character limit.

GREETING_MSG = (
    "\U0001f44b *Welcome to CropDoc!*\n"
    "\n"
    "I can help identify diseases in your Corn, Potato, and Tomato crops.\n"
    "\n"
    "\U0001f4f8 *Send me a photo* of a diseased leaf, and I will diagnose it "
    "with treatment recommendations.\n"
    "\n"
    "Type *help* for more options."
)

HELP_MSG = (
    "\U0001f33e *CropDoc \u2014 Help*\n"
    "\n"
    "\U0001f4f8 *Send a leaf photo* \u2014 Get disease diagnosis\n"
    "\U0001f4cb *crops* \u2014 See supported crops\n"
    "\u2753 *help* \u2014 Show this message\n"
    "\n"
    "*Supported crops:* Corn, Potato, Tomato\n"
    "*Supported diseases:* 15 classes\n"
    "\n"
    "\U0001f4a1 For best results, send a clear, close-up photo of a single leaf "
    "in good lighting."
)

SUPPORTED_CROPS_MSG = (
    "\U0001f33d *Supported Crops & Diseases*\n"
    "\n"
    "*Corn (4):* Common Rust, Gray Leaf Spot, Healthy, Northern Leaf Blight\n"
    "*Potato (3):* Early Blight, Healthy, Late Blight\n"
    "*Tomato (8):* Bacterial Spot, Early Blight, Healthy, Late Blight, "
    "Leaf Mold, Septoria Leaf Spot, Target Spot, Yellow Leaf Curl\n"
    "\n"
    "\U0001f4f8 Send a leaf photo to get started!"
)

ERROR_NON_IMAGE_MSG = (
    "\U0001f914 I can only analyze leaf images.\n"
    "\n"
    "Please send a *photo* (JPEG or PNG) of a Corn, Potato, or Tomato leaf.\n"
    "\n"
    "Type *help* for more info."
)

ERROR_DOWNLOAD_MSG = (
    "\u26a0\ufe0f Could not download your image. Please try sending it again."
)

ERROR_INVALID_IMAGE_MSG = (
    "\u26a0\ufe0f Could not process your image. "
    "Please send a clear JPEG or PNG photo of a leaf."
)

ERROR_RATE_LIMITED_MSG = (
    "\u23f3 You are sending requests too quickly.\n"
    "\n"
    "Please wait a moment before sending another photo. "
    "This helps us keep the service available for all farmers."
)

ERROR_GENERIC_MSG = (
    "\u26a0\ufe0f Something went wrong while analyzing your image.\n"
    "\n"
    "Please try again. If the problem continues, try sending a different photo."
)

PROMPT_SEND_PHOTO_MSG = (
    "\U0001f4f8 Send me a photo of a Corn, Potato, or Tomato leaf "
    "to get a disease diagnosis.\n"
    "\n"
    "Type *help* for more options."
)
