"""
Export PyTorch model to ONNX format for React Native deployment.

The React Native app uses onnxruntime-react-native for inference,
which supports CoreML (iOS) and NNAPI (Android) hardware acceleration.

Usage:
    cd crop-prediction
    python mobile/scripts/export_model.py

Requirements:
    pip install torch torchvision onnx onnxscript

Output:
    mobile/assets/model/crop_disease_classifier.onnx
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.onnx
from src.models.classifier import build_model
from src.config import MODEL_PATH, IMG_SIZE

OUTPUT_DIR = PROJECT_ROOT / "mobile" / "assets" / "model"
OUTPUT_PATH = OUTPUT_DIR / "crop_disease_classifier.onnx"


def export():
    print("Loading trained model ...")
    model, _, _ = build_model(num_classes=15, device=torch.device("cpu"))
    model.load_state_dict(
        torch.load(str(MODEL_PATH), map_location="cpu", weights_only=True)
    )
    model.eval()
    print(f"  Checkpoint: {MODEL_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Exporting to ONNX ...")
    sample_input = torch.randn(1, 3, IMG_SIZE, IMG_SIZE)
    torch.onnx.export(
        model,
        sample_input,
        str(OUTPUT_PATH),
        opset_version=17,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes=None,  # Fixed batch size of 1
    )

    size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"  Exported: {OUTPUT_PATH}")
    print(f"  Size: {size_mb:.1f} MB")

    # Verify the model
    import onnx
    onnx_model = onnx.load(str(OUTPUT_PATH))
    onnx.checker.check_model(onnx_model)
    print("  Model verification: PASSED")

    print("\nDone! The ONNX model is ready for React Native deployment.")
    print("Next steps:")
    print("  iOS:     Add crop_disease_classifier.onnx to Xcode bundle resources")
    print("  Android: Place in android/app/src/main/assets/model/")


if __name__ == "__main__":
    export()
