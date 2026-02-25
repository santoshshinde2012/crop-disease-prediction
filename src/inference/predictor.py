"""Inference predictor for the Streamlit app."""
import json

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

from src.config import IMG_SIZE, MODEL_PATH, METRICS_DIR, IMAGENET_MEAN, IMAGENET_STD

DISEASE_INFO = {
    "Corn: Common Rust": "Apply fungicide (e.g., azoxystrobin). Remove severely affected leaves.",
    "Corn: Gray Leaf Spot": "Use resistant hybrids. Apply foliar fungicides if severity is high.",
    "Corn: Healthy": "No disease detected. Continue regular monitoring.",
    "Corn: Northern Leaf Blight": "Apply fungicide at early stages. Rotate crops to reduce inoculum.",
    "Potato: Early Blight": "Apply chlorothalonil or mancozeb fungicide. Ensure proper spacing.",
    "Potato: Healthy": "No disease detected. Continue regular monitoring.",
    "Potato: Late Blight": "URGENT: Apply metalaxyl-based fungicide immediately. Remove infected plants.",
    "Tomato: Bacterial Spot": "Apply copper-based bactericide. Avoid overhead irrigation.",
    "Tomato: Early Blight": "Apply chlorothalonil fungicide. Mulch around base to prevent spore splash.",
    "Tomato: Healthy": "No disease detected. Continue regular monitoring.",
    "Tomato: Late Blight": "URGENT: Apply fungicide immediately. Remove and destroy infected tissue.",
    "Tomato: Leaf Mold": "Improve ventilation. Apply fungicide if greenhouse-grown.",
    "Tomato: Septoria Leaf Spot": "Remove infected lower leaves. Apply fungicide preventively.",
    "Tomato: Target Spot": "Apply chlorothalonil. Maintain good air circulation.",
    "Tomato: Yellow Leaf Curl": "Control whitefly vectors. Remove infected plants to prevent spread.",
}


class DiseasePredictor:
    """Encapsulates model loading, preprocessing, and prediction."""

    def __init__(self, model_path=None, class_names_path=None, device=None):
        self.model_path = model_path or MODEL_PATH
        self.class_names_path = class_names_path or (METRICS_DIR / "class_names.json")
        self.device = device or torch.device("cpu")

        with open(self.class_names_path) as f:
            self.class_names = json.load(f)
        self.num_classes = len(self.class_names)

        self.model = self._load_model()

        self.preprocess = transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ])

    def _load_model(self):
        model = models.mobilenet_v2(weights=None)
        model.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(model.last_channel, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, self.num_classes),
        )
        model.load_state_dict(
            torch.load(self.model_path, map_location=self.device, weights_only=True)
        )
        model.eval()
        return model.to(self.device)

    def predict(self, image: Image.Image, top_k: int = 5):
        """Run prediction on a PIL Image.

        Returns dict with keys: top_class, confidence, top_k_probs, recommendation.
        """
        input_tensor = self.preprocess(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            probs = torch.softmax(outputs, dim=1)[0]

        top_indices = torch.argsort(probs, descending=True)[:top_k]
        top_k_probs = {
            self.class_names[i]: float(probs[i]) for i in top_indices
        }

        top_class = self.class_names[top_indices[0]]
        confidence = float(probs[top_indices[0]])
        recommendation = DISEASE_INFO.get(
            top_class, "Consult a local agronomist for specific treatment."
        )

        return {
            "top_class": top_class,
            "confidence": confidence,
            "top_k_probs": top_k_probs,
            "recommendation": recommendation,
        }
