# Mobile Deployment: React Native + On-Device ML

## What We Have

Our trained PyTorch model that classifies crop leaf diseases:

| Detail | Value | Source File |
|--------|-------|-------------|
| Architecture | MobileNetV2 + custom head | `src/models/classifier.py` |
| Input | 224 x 224 RGB image | `src/config.py` |
| Output | 15 class probabilities | `src/config.py` |
| Model size | 9.3 MB (.pth) | `checkpoints/best_model.pth` |
| Accuracy | 97.83% | `outputs/metrics/results.json` |

**Preprocessing** (must be replicated on-device):
```
Resize to 224x224 → Scale to [0,1] → Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
```

**15 Classes**: 8 Tomato, 3 Potato, 4 Corn diseases/healthy states.

---

## The Goal

Build a React Native app where users take a photo of a leaf and get instant disease diagnosis — **fully offline, no server needed**.

```
User takes photo → Preprocess → Model runs on phone → Show result + treatment
```

---

## Step 1: Convert the Model

React Native cannot run `.pth` files directly. We need to convert to a format that has React Native bindings. There are two viable options:

### Option A: TFLite (Recommended)

**Why**: Best React Native library support via `react-native-fast-tflite`, GPU delegate support on both platforms, smallest runtime.

```python
# scripts/export_tflite.py
import torch
import ai_edge_torch
from src.models.classifier import build_model
from src.config import MODEL_PATH, IMG_SIZE

model, _, _ = build_model(num_classes=15, device=torch.device("cpu"))
model.load_state_dict(torch.load(str(MODEL_PATH), map_location="cpu", weights_only=True))
model.eval()

sample_input = (torch.randn(1, 3, IMG_SIZE, IMG_SIZE),)
edge_model = ai_edge_torch.convert(model, sample_input)
edge_model.export("crop_disease_classifier.tflite")
```

**Install**: `pip install ai-edge-torch`
**Output**: `crop_disease_classifier.tflite` (~9 MB, or ~4.5 MB with FP16)

### Option B: ONNX

**Why**: Official `onnxruntime-react-native` package from Microsoft, mature ecosystem.

```python
# scripts/export_onnx.py
import torch
from src.models.classifier import build_model
from src.config import MODEL_PATH, IMG_SIZE

model, _, _ = build_model(num_classes=15, device=torch.device("cpu"))
model.load_state_dict(torch.load(str(MODEL_PATH), map_location="cpu", weights_only=True))
model.eval()

torch.onnx.export(
    model,
    torch.randn(1, 3, IMG_SIZE, IMG_SIZE),
    "crop_disease_classifier.onnx",
    opset_version=17,
    input_names=["input"],
    output_names=["output"],
)
```

**Install**: `pip install torch`
**Output**: `crop_disease_classifier.onnx` (~9 MB)

### Which to Pick?

| Criteria | TFLite | ONNX |
|----------|--------|------|
| RN library | `react-native-fast-tflite` | `onnxruntime-react-native` |
| GPU acceleration | Yes (CoreML delegate on iOS, GPU delegate on Android) | Yes (CoreML EP on iOS, NNAPI EP on Android) |
| Community adoption | Higher in mobile ML | Higher in general ML |
| Model size (FP16) | ~4.5 MB | ~9 MB (FP16 less straightforward) |
| Ease of quantization | Built-in tools | Needs extra steps |

**Recommendation**: Go with **TFLite** — better size optimization, simpler quantization, and `react-native-fast-tflite` is actively maintained with GPU support.

---

## Step 2: Reduce Model Size (Optional but Recommended)

FP16 quantization halves the model with near-zero accuracy loss:

```python
# scripts/export_tflite_fp16.py
import torch
import ai_edge_torch
from src.models.classifier import build_model
from src.config import MODEL_PATH, IMG_SIZE

model, _, _ = build_model(num_classes=15, device=torch.device("cpu"))
model.load_state_dict(torch.load(str(MODEL_PATH), map_location="cpu", weights_only=True))
model.eval()

sample_input = (torch.randn(1, 3, IMG_SIZE, IMG_SIZE),)
edge_model = ai_edge_torch.convert(model, sample_input)

# FP16 quantization
edge_model.set_default_optimization(ai_edge_torch.quantize.Precision.FLOAT16)
edge_model.export("crop_disease_classifier_fp16.tflite")
```

| Version | Size | Accuracy Impact |
|---------|------|-----------------|
| FP32 (original) | ~9 MB | 97.83% (baseline) |
| FP16 | ~4.5 MB | < 0.1% loss |
| INT8 (advanced) | ~2.5 MB | 1-2% loss |

FP16 is the sweet spot — half the size, same accuracy.

---

## Step 3: React Native Project Setup

### Install Dependencies

```bash
npx react-native init CropDiseaseApp
cd CropDiseaseApp

# Camera
npm install react-native-vision-camera

# ML inference
npm install react-native-fast-tflite

# Image manipulation (for preprocessing)
npm install react-native-image-resizer

cd ios && pod install
```

### Bundle the Model and Data

Place these files in the app:

```
CropDiseaseApp/
├── assets/
│   ├── model/
│   │   └── crop_disease_classifier.tflite    # Converted model (~4.5 MB)
│   ├── class_names.json                       # From outputs/metrics/class_names.json
│   └── disease_info.json                      # From src/data/disease_info.py (as JSON)
```

**class_names.json** — copy directly from `outputs/metrics/class_names.json`:
```json
["Corn: Common Rust", "Corn: Gray Leaf Spot", "Corn: Healthy", ...]
```

**disease_info.json** — convert `src/data/disease_info.py:DISEASE_DETAILS` to JSON:
```json
{
  "Tomato: Late Blight": {
    "crop": "Tomato",
    "severity": "High",
    "symptoms": ["Large, dark, water-soaked lesions on leaves..."],
    "treatment": "URGENT: Apply fungicide immediately...",
    "prevention": ["Avoid overhead irrigation..."]
  }
}
```

For **iOS**, add the `.tflite` file to the Xcode project bundle resources.
For **Android**, place it in `android/app/src/main/assets/`.

---

## Step 4: Core Inference Logic

### Loading the Model

```javascript
// src/model/classifier.js
import { loadTensorflowModel } from 'react-native-fast-tflite';
import classNames from '../../assets/class_names.json';
import diseaseInfo from '../../assets/disease_info.json';

let model = null;

export async function loadModel() {
  if (model) return model;
  model = await loadTensorflowModel(
    require('../../assets/model/crop_disease_classifier.tflite'),
    'core-ml',   // iOS: CoreML delegate, Android: auto-selects GPU/NNAPI/CPU
  );
  return model;
}
```

### Preprocessing

Our model expects: resize to 224x224, scale to [0,1], normalize with ImageNet stats.

```javascript
// src/model/preprocess.js

const MEAN = [0.485, 0.456, 0.406];
const STD  = [0.229, 0.224, 0.225];

export function preprocessImageData(rgbData, width, height) {
  // rgbData: Uint8Array of raw pixel values (RGB, 224x224)
  // Returns: Float32Array shaped [1, 3, 224, 224]

  const float32 = new Float32Array(1 * 3 * 224 * 224);

  for (let y = 0; y < 224; y++) {
    for (let x = 0; x < 224; x++) {
      const pixelIndex = (y * 224 + x) * 3;
      for (let c = 0; c < 3; c++) {
        const normalized = (rgbData[pixelIndex + c] / 255.0 - MEAN[c]) / STD[c];
        float32[c * 224 * 224 + y * 224 + x] = normalized;  // CHW layout
      }
    }
  }

  return float32;
}
```

### Running Prediction

```javascript
// src/model/predict.js
import { loadModel } from './classifier';
import { preprocessImageData } from './preprocess';
import classNames from '../../assets/class_names.json';
import diseaseInfo from '../../assets/disease_info.json';

export async function predictDisease(rgbData) {
  const model = await loadModel();

  // Preprocess: normalize with ImageNet stats
  const input = preprocessImageData(rgbData, 224, 224);

  // Run inference
  const output = await model.run([input]);
  const probabilities = output[0];  // Float32Array of 15 values

  // Softmax
  const maxVal = Math.max(...probabilities);
  const exps = probabilities.map(v => Math.exp(v - maxVal));
  const sumExps = exps.reduce((a, b) => a + b, 0);
  const softmaxProbs = exps.map(v => v / sumExps);

  // Find top prediction
  let topIndex = 0;
  for (let i = 1; i < softmaxProbs.length; i++) {
    if (softmaxProbs[i] > softmaxProbs[topIndex]) topIndex = i;
  }

  const diseaseName = classNames[topIndex];
  const confidence = softmaxProbs[topIndex];
  const details = diseaseInfo[diseaseName] || null;

  return {
    disease: diseaseName,
    confidence: confidence,
    crop: details?.crop || diseaseName.split(':')[0].trim(),
    severity: details?.severity || 'Unknown',
    treatment: details?.treatment || 'Consult a local agronomist.',
    symptoms: details?.symptoms || [],
    prevention: details?.prevention || [],
  };
}
```

---

## Step 5: Camera Integration

Using `react-native-vision-camera` for photo capture:

```javascript
// src/screens/CameraScreen.js
import React, { useRef, useState } from 'react';
import { View, TouchableOpacity, Text, Alert } from 'react-native';
import { Camera, useCameraDevice } from 'react-native-vision-camera';
import { predictDisease } from '../model/predict';

export default function CameraScreen({ navigation }) {
  const camera = useRef(null);
  const device = useCameraDevice('back');
  const [loading, setLoading] = useState(false);

  const captureAndPredict = async () => {
    if (!camera.current || loading) return;
    setLoading(true);

    try {
      // Take photo
      const photo = await camera.current.takePhoto({ qualityPrioritization: 'speed' });

      // Resize to 224x224 and get pixel data
      // (use react-native-image-resizer or a frame processor plugin)
      const rgbData = await getResizedPixelData(photo.path, 224, 224);

      // Run prediction
      const result = await predictDisease(rgbData);

      if (result.confidence < 0.85) {
        Alert.alert(
          'Low Confidence',
          'Could not identify the disease clearly. Please retake with better lighting.',
        );
      } else {
        navigation.navigate('Result', { result });
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to analyze image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!device) return <Text>No camera available</Text>;

  return (
    <View style={{ flex: 1 }}>
      <Camera ref={camera} device={device} photo={true} style={{ flex: 1 }} isActive={true} />
      <TouchableOpacity onPress={captureAndPredict} disabled={loading}>
        <Text>{loading ? 'Analyzing...' : 'Take Photo'}</Text>
      </TouchableOpacity>
    </View>
  );
}
```

### Real-Time Frame Processing (Optional)

For live camera analysis using VisionCamera frame processors:

```javascript
import { useFrameProcessor } from 'react-native-vision-camera';
import { useTensorflowModel } from 'react-native-fast-tflite';

// Inside component:
const model = useTensorflowModel(
  require('../../assets/model/crop_disease_classifier.tflite'),
);

const frameProcessor = useFrameProcessor((frame) => {
  'worklet';
  if (!model) return;

  // react-native-fast-tflite can run directly on camera frames
  const result = model.runSync(frame);
  // Process result...
}, [model]);

// <Camera frameProcessor={frameProcessor} ... />
```

---

## Step 6: Offline-First Design

Everything runs on-device. No internet needed for:

| Feature | How It Works Offline |
|---------|---------------------|
| Disease prediction | Model bundled in app binary |
| Treatment info | `disease_info.json` bundled in app |
| Prediction history | Stored in local AsyncStorage or SQLite |

### Local Storage for History

```javascript
// src/storage/history.js
import AsyncStorage from '@react-native-async-storage/async-storage';

export async function savePrediction(result, imagePath) {
  const entry = {
    id: Date.now().toString(),
    disease: result.disease,
    confidence: result.confidence,
    treatment: result.treatment,
    imagePath: imagePath,
    timestamp: new Date().toISOString(),
    synced: false,
  };

  const history = JSON.parse(await AsyncStorage.getItem('predictions') || '[]');
  history.unshift(entry);
  await AsyncStorage.setItem('predictions', JSON.stringify(history));
  return entry;
}

export async function getHistory() {
  return JSON.parse(await AsyncStorage.getItem('predictions') || '[]');
}
```

### Sync When Online (Optional)

```javascript
// src/storage/sync.js
import NetInfo from '@react-native-community/netinfo';

export async function syncPendingPredictions(apiBaseUrl) {
  const netState = await NetInfo.fetch();
  if (!netState.isConnected) return;

  const history = await getHistory();
  const unsynced = history.filter(entry => !entry.synced);

  for (const entry of unsynced) {
    try {
      await fetch(`${apiBaseUrl}/api/v1/predictions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry),
      });
      entry.synced = true;
    } catch {
      break;  // Stop on first failure, retry later
    }
  }

  await AsyncStorage.setItem('predictions', JSON.stringify(history));
}
```

---

## App Architecture Summary

```
CropDiseaseApp/
├── assets/
│   ├── model/crop_disease_classifier.tflite   # 4.5 MB (FP16)
│   ├── class_names.json                        # < 1 KB
│   └── disease_info.json                       # ~15 KB
├── src/
│   ├── model/
│   │   ├── classifier.js       # Load TFLite model
│   │   ├── preprocess.js       # ImageNet normalization
│   │   └── predict.js          # Run inference + parse results
│   ├── screens/
│   │   ├── CameraScreen.js     # Take photo + predict
│   │   ├── ResultScreen.js     # Show disease + treatment
│   │   └── HistoryScreen.js    # Past predictions
│   └── storage/
│       ├── history.js          # AsyncStorage for predictions
│       └── sync.js             # Upload when online
├── android/app/src/main/assets/
│   └── crop_disease_classifier.tflite          # Android bundle
├── ios/
│   └── crop_disease_classifier.tflite          # iOS bundle resource
└── package.json
```

**Total on-device footprint**: ~4.5 MB (model) + ~16 KB (data) = **~4.5 MB**

---

## Expected Performance

| Device | Inference Time | Notes |
|--------|---------------|-------|
| iPhone 12+ (A14+) | ~5 ms | CoreML delegate, Neural Engine |
| iPhone 8–11 | ~15 ms | CoreML delegate |
| Pixel 6+ | ~25 ms | GPU delegate |
| Mid-range Android | ~60 ms | CPU with XNNPACK |
| Low-end Android | ~120 ms | CPU only |

All well under the 500 ms threshold for "instant" feel.

---

## Key Dependencies

```json
{
  "react-native-vision-camera": "^4.x",
  "react-native-fast-tflite": "^1.x",
  "react-native-image-resizer": "^3.x",
  "@react-native-async-storage/async-storage": "^1.x",
  "@react-native-community/netinfo": "^11.x"
}
```

**Python (for model export only)**:
```
ai-edge-torch
torch
```

---

## Implementation Checklist

1. **Export model** — Run `scripts/export_tflite.py` to get `.tflite` file
2. **Quantize to FP16** — Halves size from 9 MB to 4.5 MB
3. **Set up React Native project** — Install camera + TFLite libraries
4. **Bundle assets** — Model file, class names, disease info JSON
5. **Build inference pipeline** — Preprocess (resize + normalize) → model.run → softmax → result
6. **Camera screen** — Capture photo, run prediction, show result
7. **Result screen** — Display disease name, confidence, treatment, prevention
8. **History** — Save predictions locally with AsyncStorage
9. **Test on devices** — Verify inference speed and accuracy on real phones
10. **Optional: Sync** — Upload predictions to backend API when online

---

## References

- **react-native-fast-tflite**: https://github.com/mrousavy/react-native-fast-tflite
- **react-native-vision-camera**: https://github.com/mrousavy/react-native-vision-camera
- **onnxruntime-react-native**: https://onnxruntime.ai/docs/tutorials/react-native
- **ai-edge-torch**: https://github.com/google-ai-edge/ai-edge-torch
- **Our model code**: `src/models/classifier.py`, `src/inference/predictor.py`, `src/config.py`
- **Our disease data**: `src/data/disease_info.py`
