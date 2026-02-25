"""
Export PyTorch model to TFLite format for mobile deployment.

The React Native app uses react-native-fast-tflite for inference,
which supports CoreML (iOS) and GPU delegate (Android) hardware acceleration.

Conversion path: PyTorch (.pth) → ONNX → TFLite (via onnx2tf)

Usage:
    cd crop-prediction
    pip install torch torchvision onnx==1.16.2 onnx2tf tensorflow
    python scripts/export_model.py

Output:
    exports/crop_disease_classifier.tflite          (canonical export)
    mobile/assets/model/crop_disease_classifier.tflite  (copy for Metro bundling)
"""

import sys
import shutil
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
from src.models.classifier import build_model
from src.config import MODEL_PATH, IMG_SIZE

EXPORTS_DIR = PROJECT_ROOT / "exports"
TFLITE_PATH = EXPORTS_DIR / "crop_disease_classifier.tflite"
MOBILE_MODEL_DIR = PROJECT_ROOT / "mobile" / "assets" / "model"


def export():
    print("Loading trained model ...")
    model, _, _ = build_model(num_classes=15, device=torch.device("cpu"))
    model.load_state_dict(
        torch.load(str(MODEL_PATH), map_location="cpu", weights_only=True)
    )
    model.eval()
    print(f"  Checkpoint: {MODEL_PATH}")

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        onnx_path = Path(tmpdir) / "model.onnx"

        # Step 1: PyTorch → ONNX (use legacy TorchScript exporter for compatibility)
        print("\nStep 1: Exporting PyTorch → ONNX ...")
        dummy_input = torch.randn(1, 3, IMG_SIZE, IMG_SIZE)
        torch.onnx.export(
            model,
            dummy_input,
            str(onnx_path),
            opset_version=13,
            input_names=["input"],
            output_names=["output"],
            dynamo=False,
        )
        onnx_size = onnx_path.stat().st_size / (1024 * 1024)
        print(f"  ONNX: {onnx_path} ({onnx_size:.1f} MB)")

        # Step 2: ONNX → TFLite (via onnx2tf)
        print("\nStep 2: Converting ONNX → TFLite (via onnx2tf) ...")
        import onnx2tf

        tf_out_dir = Path(tmpdir) / "tf_output"
        onnx2tf.convert(
            input_onnx_file_path=str(onnx_path),
            output_folder_path=str(tf_out_dir),
            non_verbose=True,
            copy_onnx_input_output_names_to_tflite=True,
        )

        # onnx2tf produces a .tflite file in the output folder
        generated_tflite = tf_out_dir / "model_float32.tflite"
        if not generated_tflite.exists():
            # Fallback: look for any .tflite file
            tflite_files = list(tf_out_dir.glob("*.tflite"))
            if not tflite_files:
                raise FileNotFoundError(
                    f"No .tflite file found in {tf_out_dir}"
                )
            generated_tflite = tflite_files[0]

        shutil.copy2(str(generated_tflite), str(TFLITE_PATH))
        tflite_size = TFLITE_PATH.stat().st_size / (1024 * 1024)
        print(f"  TFLite: {TFLITE_PATH} ({tflite_size:.1f} MB)")

    # Step 3: Verify the TFLite model
    print("\nStep 3: Verifying TFLite model ...")
    import numpy as np
    import tensorflow as tf

    interpreter = tf.lite.Interpreter(model_path=str(TFLITE_PATH))
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    input_shape = input_details[0]["shape"]
    output_shape = output_details[0]["shape"]
    print(f"  Input shape:  {input_shape}")
    print(f"  Output shape: {output_shape}")

    test_input = np.random.randn(*input_shape).astype(np.float32)
    interpreter.set_tensor(input_details[0]["index"], test_input)
    interpreter.invoke()
    test_output = interpreter.get_tensor(output_details[0]["index"])
    print(f"  Test output shape: {test_output.shape}")
    assert test_output.shape[-1] == 15, (
        f"Expected 15 classes, got {test_output.shape[-1]}"
    )
    print("  Model verification: PASSED")

    # Step 4: Copy to mobile assets for Metro bundling
    print("\nStep 4: Copying to mobile assets ...")
    MOBILE_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    mobile_tflite = MOBILE_MODEL_DIR / "crop_disease_classifier.tflite"
    shutil.copy2(str(TFLITE_PATH), str(mobile_tflite))
    print(f"  Copied to: {mobile_tflite}")

    print(f"\nDone! TFLite model ready:")
    print(f"  Export:  {TFLITE_PATH} ({tflite_size:.1f} MB)")
    print(f"  Mobile:  {mobile_tflite}")
    print("\nNext steps:")
    print("  cd mobile && npm install && cd ios && pod install && cd ..")
    print("  npx react-native start --reset-cache")


if __name__ == "__main__":
    export()
