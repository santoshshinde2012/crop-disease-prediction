"""TFLite inference predictor for lightweight on-device style prediction."""
import json

import numpy as np
from PIL import Image

from src.config import IMG_SIZE, METRICS_DIR, IMAGENET_MEAN, IMAGENET_STD

TFLITE_MODEL_PATH = "exports/crop_disease_classifier.tflite"

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


class TFLitePredictor:
    """Lightweight predictor using TensorFlow Lite runtime."""

    def __init__(self, model_path=None, class_names_path=None):
        # Try multiple TFLite backends in order of preference
        try:
            import tflite_runtime.interpreter as tflite
        except ImportError:
            try:
                import tensorflow.lite as tflite
            except ImportError:
                from tensorflow import lite as tflite

        from pathlib import Path
        project_root = Path(__file__).resolve().parent.parent.parent
        self.model_path = model_path or str(project_root / TFLITE_MODEL_PATH)
        self.class_names_path = class_names_path or (METRICS_DIR / "class_names.json")

        with open(self.class_names_path) as f:
            self.class_names = json.load(f)
        self.num_classes = len(self.class_names)

        self.interpreter = tflite.Interpreter(model_path=self.model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def _preprocess(self, image: Image.Image) -> np.ndarray:
        """Resize, normalize, and format image for TFLite input."""
        img = image.resize((IMG_SIZE, IMG_SIZE))
        arr = np.array(img, dtype=np.float32) / 255.0
        mean = np.array(IMAGENET_MEAN, dtype=np.float32)
        std = np.array(IMAGENET_STD, dtype=np.float32)
        arr = (arr - mean) / std
        # TFLite expects NHWC by default, but check input shape
        input_shape = self.input_details[0]["shape"]
        if input_shape[-1] == 3:
            # NHWC format
            arr = np.expand_dims(arr, axis=0)
        else:
            # NCHW format
            arr = np.transpose(arr, (2, 0, 1))
            arr = np.expand_dims(arr, axis=0)
        return arr.astype(np.float32)

    def predict(self, image: Image.Image, top_k: int = 5) -> dict:
        """Run prediction on a PIL Image.

        Returns dict with keys: top_class, confidence, top_k_probs, recommendation.
        """
        input_data = self._preprocess(image)
        self.interpreter.set_tensor(self.input_details[0]["index"], input_data)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]["index"])[0]

        # softmax
        exp_scores = np.exp(output_data - np.max(output_data))
        probs = exp_scores / exp_scores.sum()

        top_indices = np.argsort(probs)[::-1][:top_k]
        top_k_probs = {self.class_names[i]: float(probs[i]) for i in top_indices}

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
