# Crop Disease Classification

A deep learning pipeline to classify plant diseases from leaf images using the PlantVillage dataset. Built with **MobileNetV2 transfer learning** in PyTorch, achieving **97.8% validation accuracy** across 15 disease classes — optimized for mobile deployment in farmer-facing application.

### System Overview

<p align="center">
  <img src="wiki/images/PlantVillage%20Dataset.png" alt="System Overview — PlantVillage → ML Pipeline → Streamlit, FastAPI, Mobile" />
</p>

> PlantVillage dataset trains a MobileNetV2 model. The PyTorch model serves Streamlit and FastAPI directly. An export script converts it to TFLite for the React Native mobile app.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Structure](#project-structure)
3. [Setup Instructions](#setup-instructions)
4. [Running the Notebook](#running-the-notebook)
5. [Running the Streamlit App](#running-the-streamlit-app)
6. [Running the REST API](#running-the-rest-api)
7. [Docker Deployment](#docker-deployment)
8. [WhatsApp Integration](#whatsapp-integration)
9. [Mobile App (React Native)](#mobile-app-react-native)
10. [Dataset](#dataset)
11. [Approach](#approach)
12. [Model Architecture](#model-architecture)
13. [Training Strategy](#training-strategy)
14. [Model Performance](#model-performance)
15. [Visualizations](#visualizations)
16. [Business Recommendation](#business-recommendation)
17. [Documentation](#documentation)

---

## Quick Start

```bash
# 1. Clone and navigate to project
cd crop-prediction

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download dataset (requires Kaggle API key)
kaggle datasets download -d abdallahalidev/plantvillage-dataset
unzip -q plantvillage-dataset.zip -d plantvillage-dataset

# 4. Create data symlink
mkdir -p data/raw
ln -sf "$(pwd)/plantvillage-dataset/plantvillage dataset/color" data/raw/color

# 5. Run the notebook (primary deliverable)
cd notebooks && jupyter notebook crop_disease_classification.ipynb

# 6. Launch the Streamlit demo app (bonus)
cd .. && streamlit run streamlit_app/app.py

# 7. Launch the REST API (from project root)
uvicorn api.main:app --reload

# 8. Launch via Docker (alternative to step 7)
cp .env.example .env   # edit with your config
docker compose up --build

# 9. Run the mobile app (React Native)
pip install torch torchvision onnx==1.16.2 onnx2tf tensorflow && python scripts/export_model.py
cd mobile && npm install && cd ios && pod install && cd .. && npx react-native run-ios
```

---

## Project Structure

The codebase follows **SOLID principles** with clear separation of concerns:

```
crop-prediction/
├── .streamlit/
│   └── config.toml                        # Streamlit theme (green agricultural palette)
├── src/                                   # Shared ML pipeline (SOLID principles)
│   ├── __init__.py
│   ├── config.py                          # Central config (paths, hyperparameters, constants)
│   ├── data/                              # SRP: Data loading & transforms
│   │   ├── transforms.py                  #   Image transform pipelines
│   │   ├── dataset.py                     #   TransformSubset class, dataset preparation
│   │   ├── loader.py                      #   DataLoader creation, class counting
│   │   └── disease_info.py                #   Enriched disease data (shared across apps)
│   ├── models/                            # SRP: Model architecture
│   │   └── classifier.py                  #   MobileNetV2 build & layer unfreezing
│   ├── training/                          # SRP: Training logic
│   │   └── trainer.py                     #   Two-phase training with early stopping
│   ├── evaluation/                        # SRP: Evaluation & export
│   │   ├── metrics.py                     #   Prediction collection, classification report
│   │   ├── benchmark.py                   #   Inference speed benchmarking
│   │   └── export.py                      #   Save results (JSON, CSV)
│   ├── visualization/                     # SRP: All plotting in one place
│   │   ├── data_plots.py                  #   Class distribution, sample images, augmentation
│   │   ├── training_plots.py              #   Training history curves
│   │   └── eval_plots.py                  #   Confusion matrix, predictions, per-class accuracy
│   └── inference/                         # SRP: Inference for deployment
│       ├── predictor.py                   #   DiseasePredictor class (PyTorch)
│       └── tflite_predictor.py            #   TFLitePredictor class (lightweight runtime)
├── api/                                   # FastAPI REST API
│   ├── main.py                            #   App entry, lifespan, CORS, middleware, routers
│   ├── config.py                          #   API config (dotenv, CORS, rate limits, Twilio)
│   ├── dependencies.py                    #   Dependency injection (predictor, Twilio validation)
│   ├── exceptions.py                      #   Custom exceptions + handlers
│   ├── schemas/                           #   Pydantic v2 response models
│   │   ├── error.py                       #     ErrorResponse (unified error envelope)
│   │   ├── health.py                      #     HealthResponse
│   │   ├── prediction.py                  #     PredictionResponse, TopKPrediction
│   │   ├── disease.py                     #     DiseaseDetailResponse, DiseaseListResponse
│   │   └── whatsapp.py                    #     TwilioWebhookData, message templates
│   ├── routers/                           #   API endpoint modules
│   │   ├── health.py                      #     GET  /health/live, /health
│   │   ├── prediction.py                  #     POST /predict (async, rate-limited)
│   │   ├── diseases.py                    #     GET  /diseases
│   │   └── whatsapp.py                    #     POST /whatsapp/webhook (Twilio)
│   └── services/
│       └── whatsapp_service.py            #   WhatsApp: image download, response formatting
├── streamlit_app/                         # Streamlit demo app (Part 4 Bonus)
│   ├── app.py                             #   Entry point — multi-page navigation
│   ├── styles.py                          #   Custom CSS design system
│   ├── components.py                      #   Reusable UI: cards, bars, badges, chips
│   └── views/                             #   Page modules
│       ├── predict.py                     #     Diagnosis: 3 inference modes, multi-compare
│       ├── dashboard.py                   #     Model performance metrics & plots
│       └── disease_library.py             #     Browsable disease catalog
├── mobile/                                # React Native mobile app (online + offline)
│   ├── App.tsx                            #   Entry point: Providers → Navigation
│   ├── assets/data/                       #   Bundled class names + disease info JSON
│   ├── assets/model/                      #   Bundled TFLite model for offline inference
│   ├── src/screens/                       #   Home, Camera, Result, History, Library
│   ├── src/components/                    #   Reusable UI (Card, Button, Badge, ModeToggle)
│   ├── src/context/                       #   React contexts
│   │   ├── ModelContext.tsx               #     TFLite model lifecycle (load, run, isReady)
│   │   └── InferenceModeContext.tsx       #     Online/offline mode with AsyncStorage persistence
│   ├── src/hooks/usePrediction.ts         #   Orchestrates offline or online prediction pipeline
│   ├── src/services/classifier.ts         #   TFLite model load + on-device inference
│   ├── src/services/apiClient.ts          #   Online prediction via REST API (fetch + FormData)
│   ├── src/services/imageProcessor.ts     #   Image resize + pixel extraction
│   └── src/theme/                         #   Design tokens (colors, typography, spacing, shadows)
├── scripts/                               # Project-level utility scripts
│   ├── export_model.py                    #   PyTorch → TFLite conversion for mobile
│   └── sync_mobile_assets.py              #   Sync disease data to mobile assets
├── wiki/                                  # Detailed guides and documentation
│   ├── execution-guide.md                 #   End-to-end execution order for all components
│   └── architecture.md                    #   Mermaid architecture diagrams
├── checkpoints/
│   └── best_model.pth                     # Saved model weights (9.3 MB)
├── exports/
│   └── crop_disease_classifier.tflite     # TFLite model for mobile (9.1 MB)
├── data/
│   └── raw/                               # Symlink to PlantVillage color images
├── outputs/
│   ├── plots/                             # 8 PNG visualizations
│   └── metrics/                           # class_names.json, results.json, summary CSV
├── notebooks/
│   └── crop_disease_classification.ipynb  # Primary deliverable — full end-to-end pipeline
├── Dockerfile                             # Multi-stage production Docker build
├── docker-compose.yml                     # One-command Docker deployment
├── requirements.txt                       # Python dependencies
├── .env.example                           # Environment variable template
├── .gitignore
├── assignment.pdf                         # Original assignment brief
└── README.md
```

### SOLID Design Principles Applied

| Principle | Implementation |
|-----------|---------------|
| **Single Responsibility** | Each module has one job: `transforms.py` (transforms only), `trainer.py` (training only), `components.py` (UI components only) |
| **Open/Closed** | New views can be added to `streamlit_app/views/`, new API routes to `api/routers/` without modifying existing code |
| **Dependency Inversion** | Both Streamlit and FastAPI depend on `DiseasePredictor` abstraction, not raw model loading; shared disease data lives in `src/` |

---

## Setup Instructions

### Prerequisites

- **Python** 3.8+ (tested on 3.11)
- **Kaggle account** with API credentials for dataset download
- **GPU** (recommended): Apple MPS, NVIDIA CUDA, or CPU fallback

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: `torch`, `torchvision`, `matplotlib`, `seaborn`, `scikit-learn`, `pandas`, `streamlit`, `fastapi`, `uvicorn`, `gunicorn`, `python-multipart`, `python-dotenv`, `requests`, `Pillow`, `tflite-runtime`, `twilio`, `httpx`, `jupyter`

### Step 2: Configure Kaggle API

If you don't already have Kaggle API credentials:

1. Go to [kaggle.com/settings](https://www.kaggle.com/settings) and click **"Create New Token"**
2. Save the downloaded `kaggle.json` to `~/.kaggle/kaggle.json`
3. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`

### Step 3: Download the PlantVillage Dataset

```bash
kaggle datasets download -d abdallahalidev/plantvillage-dataset
unzip -q plantvillage-dataset.zip -d plantvillage-dataset
```

This downloads ~2 GB of plant leaf images (~54,000 images across 38 classes).

### Step 4: Create Data Symlink

```bash
mkdir -p data/raw
ln -sf "$(pwd)/plantvillage-dataset/plantvillage dataset/color" data/raw/color
```

This creates a symlink so the pipeline can access the images at `data/raw/color/`.

---

## Running the Notebook

The Jupyter notebook is the **primary deliverable** — it contains the full end-to-end pipeline with inline visualizations, markdown explanations, and business recommendations.

```bash
cd notebooks
jupyter notebook crop_disease_classification.ipynb
```

Run all cells sequentially from top to bottom. The notebook covers all 4 parts of the assignment:

| Part | Description | Output |
|------|-------------|--------|
| **Part 1: Data Exploration** | Class distribution, sample images, dataset insights | `outputs/plots/class_distribution.png`, `sample_images.png` |
| **Part 2: Model Building** | Data augmentation, MobileNetV2 build, two-phase training | `checkpoints/best_model.pth`, `outputs/plots/training_history.png` |
| **Part 3: Evaluation & Business Impact** | Confusion matrix, correct/incorrect predictions, deployment analysis, business recommendation | `outputs/plots/*.png`, `outputs/metrics/*.json` |
| **Part 4: Bonus** | Streamlit demo app reference | `streamlit_app/` |

The notebook imports all logic from `src/` packages (no code duplication), following SOLID principles.

### Expected Runtime
- **GPU (MPS/CUDA)**: ~10-15 minutes
- **CPU**: ~30-45 minutes

---

## Running the Streamlit App

A professional multi-page web app for real-time disease diagnosis (Part 4 Bonus):

```bash
streamlit run streamlit_app/app.py
```

Open **http://localhost:8501** in your browser. The app has **3 pages**:

| Page | Description |
|------|-------------|
| **Diagnosis** | Upload a leaf image to get disease identification with confidence scores and treatment recommendations |
| **Model Performance** | Dashboard with accuracy metrics, confusion matrix, training history, and per-class performance |
| **Disease Library** | Browse all 15 disease classes with symptoms, treatment, and prevention — filterable by crop |

### Three Inference Modes

The Diagnosis page supports **three inference modes** that can be selected independently via compact chip toggles — enable multiple modes simultaneously to compare results side-by-side:

| Mode | Engine | Use Case |
|------|--------|----------|
| **Local Model** | Full PyTorch MobileNetV2 | Highest accuracy, GPU-accelerated |
| **TFLite** | TensorFlow Lite runtime | Lightweight, minimal dependencies |
| **Online API** | REST API call | Delegates to the FastAPI server |

When multiple modes are selected, results are shown in parallel columns with per-mode inference time, confidence scores, and top-5 predictions for easy comparison.

**Features:**
- **Multi-mode comparison** — run up to 3 inference engines simultaneously and compare results
- **API health indicator** — real-time connection status pill when Online mode is selected
- Custom CSS design system with green agricultural theme
- Reusable UI components (metric cards, confidence bars, severity badges, disease cards, mode chips)
- Multi-page navigation with `st.navigation()` API
- Models cached via `@st.cache_resource` for instant predictions

> **Note**: The app requires a trained model (`checkpoints/best_model.pth`) and class names (`outputs/metrics/class_names.json`). Run the notebook first if these don't exist. TFLite mode requires `exports/crop_disease_classifier.tflite`. For Online mode, the REST API must be running (`uvicorn api.main:app`).

### Inference Flow (All Consumers)

<p align="center">
  <img src="wiki/images/Inference%20Flow.png" alt="Inference Flow — Streamlit, REST API, and Mobile App with online/offline mode" />
</p>

> Streamlit and Mobile support **multiple inference modes**. Offline uses local models (PyTorch / TFLite). Online delegates to the REST API. The arrows between groups show the online mode delegation path.

---

## Running the REST API

A production-ready FastAPI application with OpenAPI documentation, request tracing, and rate limiting:

```bash
# Development
uvicorn api.main:app --reload

# Production
gunicorn api.main:app -k uvicorn.workers.UvicornWorker --workers 2

# Docker (see Docker Deployment section)
docker compose up --build
```

> **Important**: Always run from the **project root** directory, not from inside `api/`.

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Interactive Swagger UI |
| http://localhost:8000/redoc | ReDoc documentation |
| http://localhost:8000/openapi.json | Raw OpenAPI 3.1 spec |

### API Endpoints

All endpoints are versioned under `/api/v1/`.

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| `GET`  | `/api/v1/health` | Readiness check with model status and version | `200`, `503` |
| `GET`  | `/api/v1/health/live` | Liveness probe (for container orchestrators) | `200` |
| `POST` | `/api/v1/predict` | Upload leaf image for disease prediction | `200`, `400`, `413`, `422`, `429`, `503` |
| `GET`  | `/api/v1/diseases` | List all 15 disease classes (optional `?crop=` filter) | `200` |
| `GET`  | `/api/v1/diseases/{disease_name}` | Get detailed info for a specific disease | `200`, `404` |
| `POST` | `/api/v1/whatsapp/webhook` | Twilio WhatsApp webhook for crop diagnosis | `200` |

### Production Features

- **Request ID tracing** — every request/response includes an `X-Request-ID` header (auto-generated or pass your own)
- **Per-IP rate limiting** — prediction endpoint limited to 30 req/min (configurable via `PREDICT_RATE_LIMIT_PER_MINUTE`)
- **Async file handling** — prediction endpoint uses `await file.read()` for non-blocking I/O
- **Configurable CORS** — origins set via `CORS_ORIGINS` environment variable
- **Structured logging** — request method, path, status code, latency, and request ID on every request
- **Environment config** — all settings loaded from `.env` via `python-dotenv`

### Example: Predict Disease

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -F "file=@leaf_image.jpg" \
  -F "top_k=5"
```

**Success response** (`200`):

```json
{
  "success": true,
  "prediction": "Tomato: Early Blight",
  "confidence": 0.9523,
  "crop": "Tomato",
  "severity": "Moderate",
  "treatment": "Apply chlorothalonil fungicide. Mulch around base to prevent spore splash.",
  "top_k": [
    {"class_name": "Tomato: Early Blight", "confidence": 0.9523},
    {"class_name": "Tomato: Late Blight", "confidence": 0.0234},
    {"class_name": "Tomato: Septoria Leaf Spot", "confidence": 0.0102}
  ]
}
```

**Error response** (`400` / `413` / `422`):

```json
{
  "success": false,
  "error_code": "INVALID_IMAGE",
  "detail": "The uploaded file could not be processed as an image. Please upload a valid JPEG or PNG file."
}
```

### Example: List Diseases

```bash
# All diseases
curl http://localhost:8000/api/v1/diseases

# Filter by crop
curl http://localhost:8000/api/v1/diseases?crop=Potato

# Single disease
curl http://localhost:8000/api/v1/diseases/Tomato:%20Late%20Blight
```

### Example: Health Check

```bash
curl http://localhost:8000/api/v1/health
```

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "model_classes": 15,
  "timestamp": "2026-02-24T15:18:34.350911Z"
}
```

### Error Codes

All errors return a consistent JSON envelope with `success`, `error_code`, and `detail`:

| Error Code | HTTP Status | Cause |
|------------|-------------|-------|
| `INVALID_IMAGE` | 400 | Uploaded file is not a valid JPEG/PNG image |
| `FILE_TOO_LARGE` | 413 | File exceeds 10 MB limit |
| `UNSUPPORTED_TYPE` | 422 | Content type is not `image/jpeg` or `image/png` |
| `RATE_LIMITED` | 429 | Too many prediction requests from same IP (default: 30/min) |
| `SERVICE_UNAVAILABLE` | 503 | Model not loaded (startup in progress or failed) |
| `NOT_FOUND` | 404 | Requested disease class does not exist |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

> **Note**: The API requires a trained model. Run the notebook first if `checkpoints/best_model.pth` doesn't exist. See [Project Structure](#project-structure) for the full `api/` directory layout.

---

## Docker Deployment

The API includes a production-ready multi-stage Docker setup:

```bash
# 1. Create .env from template
cp .env.example .env
# Edit .env with your settings (CORS origins, rate limits, Twilio credentials)

# 2. Build and run
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### Dockerfile

- **Multi-stage build** — separate builder and runtime stages for smaller images
- **Non-root user** — runs as `appuser` for security
- **Health check** — built-in `HEALTHCHECK` against `/api/v1/health/live`
- **Production server** — gunicorn with uvicorn workers (2 workers by default)

### docker-compose.yml

- Loads environment from `.env` file
- Read-only volume mounts for model weights (`checkpoints/`, `exports/`, `outputs/metrics/`)
- 2 GB memory limit
- Auto-restart (`unless-stopped`)

### Environment Variables

See `.env.example` for the full template:

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |
| `PREDICT_RATE_LIMIT_PER_MINUTE` | `30` | Max predictions per IP per minute |
| `TWILIO_ACCOUNT_SID` | — | Twilio account SID (for WhatsApp) |
| `TWILIO_AUTH_TOKEN` | — | Twilio auth token |
| `TWILIO_WHATSAPP_NUMBER` | — | Twilio WhatsApp sender number |
| `WHATSAPP_LOW_CONFIDENCE_THRESHOLD` | `0.60` | Below this, ask user for a clearer photo |
| `WHATSAPP_RATE_LIMIT_PER_MINUTE` | `10` | Max WhatsApp requests per phone number |
| `WHATSAPP_ENABLE_SIGNATURE_VALIDATION` | `true` | Set `false` for local dev with ngrok |

---

## WhatsApp Integration

Farmers can send leaf photos via WhatsApp to get instant disease diagnosis — no app installation required. Built with the **Twilio WhatsApp API**.

### Demo

#### Welcome & High-Confidence Diagnosis

<p align="center">
  <img src="wiki/whatsapp/Demo1.png" alt="WhatsApp Demo — Welcome message, leaf photo upload, and Tomato Bacterial Spot diagnosis (100% confidence) with treatment and prevention" width="500" />
</p>

> Farmer joins the Twilio Sandbox, receives a welcome greeting, sends a leaf photo, and gets a full diagnosis: disease name, confidence, severity, treatment, and prevention tips.

#### Low-Confidence Result

<p align="center">
  <img src="wiki/whatsapp/Demo2.png" alt="WhatsApp Demo — Low confidence result (53.7%) with tips for a better photo" width="500" />
</p>

> When confidence is below 60%, the bot flags the result as uncertain and provides tips for taking a better photo (good lighting, single leaf, avoid blur).

#### Disease Diagnosis with Prevention

<p align="center">
  <img src="wiki/whatsapp/Demo3.png" alt="WhatsApp Demo — Tomato Leaf Mold diagnosis (99.6% confidence) with treatment and prevention steps" width="500" />
</p>

> High-confidence diagnosis of Tomato: Leaf Mold (99.6%) with actionable treatment and prevention steps.

### How It Works

1. Farmer sends a photo of a diseased leaf to the WhatsApp number
2. Twilio forwards the message to the `/api/v1/whatsapp/webhook` endpoint
3. The API downloads the image, runs inference, and returns a formatted diagnosis
4. Farmer receives disease name, severity, confidence, treatment, and prevention tips

### Supported Commands

| Message | Response |
|---------|----------|
| **Photo of a leaf** | Disease diagnosis with treatment recommendations |
| `hi` / `hello` / `hey` | Welcome message with instructions |
| `help` / `?` | Available commands and tips for best results |
| `crops` / `diseases` | List of supported crops and disease classes |

### Setup

1. Create a [Twilio account](https://console.twilio.com/) and set up a WhatsApp Sandbox
2. Copy `.env.example` to `.env` and fill in your Twilio credentials:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```
3. Expose your local API via ngrok (for development):
   ```bash
   ngrok http 8000
   ```
4. Set the ngrok URL as the webhook in Twilio Console:
   - Go to **Messaging** > **Try it out** > **Send a WhatsApp message** > **Sandbox settings**
   - In the **"When a message comes in"** field, enter: `https://your-ngrok-url/api/v1/whatsapp/webhook`
   - Set Method to **POST** and click **Save**
5. Set `WHATSAPP_ENABLE_SIGNATURE_VALIDATION=false` in `.env` when using ngrok

### Safety Features

- **Per-phone rate limiting** — 10 requests per minute per phone number (configurable)
- **Low-confidence threshold** — if confidence < 60%, asks the farmer to send a clearer photo
- **Twilio signature validation** — verifies webhook authenticity in production
- **EXIF transpose** — handles phone-taken photo orientation automatically

---

## Mobile App (React Native)

A React Native app with **online/offline inference toggle** — runs disease classification on-device using **TFLite** via `react-native-fast-tflite` (CoreML on iOS, GPU delegate on Android) or sends images to the REST API for server-side prediction.

#### Model Export Pipeline

<p align="center">
  <img src="wiki/images/Model%20Export%20Pipeline.png" alt="Export Pipeline — PyTorch → ONNX → TFLite → Verify → Copy to mobile" />
</p>

### Quick Start

```bash
# 1. Export the PyTorch model to TFLite format
pip install torch torchvision onnx==1.16.2 onnx2tf tensorflow
python scripts/export_model.py
# Output: exports/crop_disease_classifier.tflite (+ copied to mobile/assets/model/)

# 2. Install JS dependencies
cd mobile
npm install

# 3. Run on iOS
cd ios && pod install && cd ..
npx react-native run-ios

# 4. Run on Android
npx react-native run-android
```

> See [`mobile/README.md`](mobile/README.md) for full setup guide, troubleshooting, and platform-specific instructions.

### Online / Offline Mode

The app supports two inference modes, switchable via a toggle on the Home and Camera screens:

| Mode | How It Works | Requires |
|------|-------------|----------|
| **Offline** (default) | Camera → Resize 224×224 → ImageNet Normalize → TFLite on-device → Result | TFLite model bundled in app |
| **Online** | Camera → Send image to REST API → Receive prediction → Result | API running at `localhost:8000` |

The selected mode persists across app restarts. When switching to online mode, the app checks API health first — if unreachable, it shows an alert and stays on offline mode.

The app bundles everything needed for offline operation:

| Asset | Size | Source |
|-------|------|--------|
| TFLite model | ~9 MB | `checkpoints/best_model.pth` → `exports/crop_disease_classifier.tflite` via `scripts/export_model.py` |
| Class names | <1 KB | `outputs/metrics/class_names.json` or `mobile/assets/data/class_names.json` |
| Disease info | ~15 KB | `src/data/disease_info.py` → converted to JSON in `mobile/assets/data/` |

### Screens

| Screen | Description |
|--------|-------------|
| **Home** | Model stats (97.8% accuracy, 15 diseases, <1s inference), online/offline toggle, feature cards, "Scan a Leaf" CTA |
| **Camera** | Full-screen camera with leaf guide circle, capture button, gallery picker; online/offline toggle overlay |
| **Result** | Disease name, severity badge, confidence %, treatment recommendations, symptoms, prevention, animated top-5 confidence bars |
| **History** | Past predictions stored locally — card list with thumbnail, disease, confidence, timestamp; swipe-to-delete |
| **Library** | Browse all 15 diseases with crop filter tabs (All/Corn/Potato/Tomato), expandable detail cards |

---

## Dataset

- **Source**: [PlantVillage Dataset](https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset) (Kaggle)
- **Total available**: ~54,000 images across 38 classes
- **Selected**: 15 classes across 3 crops 

### Selected Classes (15)

| Crop | Classes | Count |
|------|---------|-------|
| **Tomato** (8) | Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Target Spot, Yellow Leaf Curl, Healthy | 16,111 |
| **Corn** (4) | Common Rust, Gray Leaf Spot, Northern Leaf Blight, Healthy | 3,852 |
| **Potato** (3) | Early Blight, Late Blight, Healthy | 2,152 |
| **Total** | **15 classes** | **22,115 images** |

### Data Split
- **Training**: 80% (17,692 images)
- **Validation**: 20% (4,423 images)
- Stratified random split with seed=42 for reproducibility

### Class Imbalance
- **Largest class**: Tomato: Yellow Leaf Curl (5,357 images)
- **Smallest class**: Potato: Healthy (152 images)
- **Imbalance ratio**: 35.2x
- **Mitigation**: Weighted random sampling + class-weighted CrossEntropyLoss

---

## Approach

### Why Transfer Learning?

Training a CNN from scratch on ~22K images risks overfitting. Transfer learning leverages features already learned on ImageNet (1.2M images), providing:
- Strong low-level feature extractors (edges, textures, colors)
- Faster convergence with less data
- Better generalization to unseen plant images

### Why MobileNetV2?

| Criterion | MobileNetV2 | ResNet50 | EfficientNet-B0 |
|-----------|------------|----------|------------------|
| Accuracy | ~97.8% | ~98.5% | ~98.2% |
| Model Size | 9.3 MB | ~97 MB | ~20 MB |
| Parameters | 2.4M | 25.6M | 5.3M |
| Mobile Inference | ~30ms | ~150ms | ~50ms |
| Offline-ready | Yes | Impractical | Yes |

MobileNetV2 uses **depthwise separable convolutions** — achieving near-ResNet accuracy at 1/10th the size. This is critical for on-device deployment in areas with limited connectivity.

#### Model Selection for Mobile Deployment

<p align="center">
  <img src="wiki/images/Model%20Selection%20for%20Mobile%20Deployment.png" alt="Quadrant Chart — MobileNetV2 in Deploy for Mobile zone, ResNet50 in Accurate but Heavy zone" />
</p>

> MobileNetV2 sits in the **Deploy for Mobile** quadrant (small size + high accuracy), making it the clear choice for Syngenta's farmer app. ResNet50 is accurate but too heavy for on-device use. See [`wiki/architecture.md`](wiki/architecture.md#5-model-selection-for-mobile-deployment) for detailed comparison.

---

## Model Architecture

```
MobileNetV2 (pre-trained on ImageNet)
├── Feature Extractor: 17 inverted residual blocks
│   └── Last 5 blocks unfrozen for fine-tuning (Phase 2)
└── Custom Classifier Head:
    ├── Dropout(0.3)
    ├── Linear(1280 → 128)
    ├── ReLU
    ├── Dropout(0.2)
    └── Linear(128 → 15)
```

- **Input**: 224 x 224 x 3 (RGB, ImageNet-normalized)
- **Total parameters**: 2,389,775
- **Trainable (Phase 1)**: 165,903 (classifier head only)
- **Trainable (Phase 2)**: 1,847,247 (head + top 5 feature blocks)

---

## Training Strategy

<p align="center">
  <img src="wiki/images/Training%20Pipeline.png" alt="Training Pipeline — Dataset → Preprocessing → Model → Two Phase Training → Output" />
</p>

### Two-Phase Transfer Learning

**Phase 1 — Feature Extraction (5 epochs)**
- Freeze all MobileNetV2 layers
- Train only the custom classifier head
- Learning rate: 1e-3 (Adam optimizer)
- Purpose: Learn disease-specific decision boundaries using pre-trained features

**Phase 2 — Fine-Tuning (up to 10 epochs)**
- Unfreeze the last 5 feature blocks
- Fine-tune with lower learning rate: 1e-4
- Purpose: Adapt high-level features to plant disease patterns

### Data Augmentation
- Random horizontal and vertical flips
- Random rotation (±20°)
- Random zoom/scale (80%-120%)
- Color jitter (brightness ±10%, contrast ±10%)

### Regularization
- **Dropout**: 0.3 (before hidden layer) + 0.2 (before output)
- **Early stopping**: Patience of 3 epochs (monitors validation accuracy)
- **Learning rate scheduling**: ReduceLROnPlateau (factor=0.5, patience=2)

### Class Imbalance Handling
- **WeightedRandomSampler**: Oversamples minority classes during training
- **Class-weighted CrossEntropyLoss**: Penalizes misclassification of rare classes more heavily

---

## Model Performance

### Overall Metrics

| Metric | Value |
|--------|-------|
| **Validation Accuracy** | **97.83%** |
| Model Size | 9.3 MB |
| Total Parameters | 2,389,775 |
| Avg Inference Time | ~9 ms (GPU) |

### Per-Class Results

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Corn: Common Rust | 1.000 | 1.000 | 1.000 | 242 |
| Corn: Gray Leaf Spot | 0.876 | 0.955 | 0.914 | 89 |
| Corn: Healthy | 1.000 | 1.000 | 1.000 | 254 |
| Corn: Northern Leaf Blight | 0.978 | 0.937 | 0.957 | 189 |
| Potato: Early Blight | 0.995 | 0.990 | 0.992 | 200 |
| Potato: Healthy | 0.897 | 1.000 | 0.945 | 26 |
| Potato: Late Blight | 0.971 | 0.958 | 0.964 | 212 |
| Tomato: Bacterial Spot | 0.977 | 0.968 | 0.972 | 433 |
| Tomato: Early Blight | 0.901 | 0.978 | 0.938 | 186 |
| Tomato: Healthy | 0.994 | 0.990 | 0.992 | 309 |
| Tomato: Late Blight | 0.977 | 0.940 | 0.958 | 399 |
| Tomato: Leaf Mold | 0.970 | 0.994 | 0.982 | 161 |
| Tomato: Septoria Leaf Spot | 0.977 | 0.995 | 0.986 | 377 |
| Tomato: Target Spot | 0.962 | 0.973 | 0.968 | 262 |
| Tomato: Yellow Leaf Curl | 0.995 | 0.987 | 0.991 | 1084 |
| **OVERALL (weighted avg)** | **0.979** | **0.978** | **0.978** | **4423** |

### Key Observations
- **Perfect classification** (100%) on Corn: Common Rust and Corn: Healthy
- **All 15 classes exceed 90%** accuracy — no weak spots
- **Hardest class**: Corn: Gray Leaf Spot (91.4% F1) — visually similar to Northern Leaf Blight
- **Smallest class** (Potato: Healthy, 26 samples) achieves 100% recall thanks to weighted sampling

---

## Visualizations

All plots are saved to `outputs/plots/` during notebook execution.

### Class Distribution

<p align="center">
  <img src="outputs/plots/class_distribution.png" alt="Class Distribution — image count per class, color-coded by crop" />
</p>

### Training History

<p align="center">
  <img src="outputs/plots/training_history.png" alt="Training History — accuracy and loss curves across both training phases" />
</p>

### Confusion Matrix

<p align="center">
  <img src="outputs/plots/confusion_matrix.png" alt="Confusion Matrix — 15x15 heatmap of true vs predicted labels" />
</p>

### Per-Class Accuracy

<p align="center">
  <img src="outputs/plots/per_class_accuracy.png" alt="Per-Class Accuracy — bar chart with green >=90%, yellow >=80%, red <80%" />
</p>

### Additional Plots

| Plot | Description |
|------|-------------|
| `sample_images.png` | Grid of 4 sample images from 5 representative classes |
| `augmentation_examples.png` | Original vs. 9 augmented versions of the same image |
| `correct_predictions.png` | 5 highest-confidence correct predictions with images |
| `incorrect_predictions.png` | 5 highest-confidence errors (most informative failures) |

---

## Business Recommendation

For farmer-facing mobile application, I recommend deploying **MobileNetV2 with transfer learning** as the crop disease classification backbone:

1. **Production-Ready Accuracy**: 97.8% across 15 disease classes with no class below 91% — suitable for real-world field diagnosis.

2. **Mobile-Optimized**: At 9.3 MB (reducible to ~3 MB with TFLite INT8 post-training quantization), the model enables **offline functionality** — critical for farmers in rural areas with limited connectivity.

3. **Fast Inference**: ~9 ms on GPU, ~30 ms on mobile devices. Farmers get instant diagnosis from a single photo.

4. **Recommended Deployment Path**:
   - Export to **TFLite** format (done: `crop_disease_classifier.tflite`)
   - Uses **CoreML** delegate (iOS) / **GPU** delegate (Android) via `react-native-fast-tflite`
   - Apply **INT8 post-training quantization** for further size reduction (<1% accuracy loss)
   - Integrate with camera pipeline for real-time field use

5. **Scalability**: Easily extensible to all 38 PlantVillage classes and adaptable to proprietary field imagery through additional fine-tuning.

---

## Documentation

Detailed guides are available in the [`wiki/`](wiki/) directory:

| Document | Description |
|----------|-------------|
| [`execution-guide.md`](wiki/execution-guide.md) | Step-by-step execution order for running all components end-to-end (notebook → Streamlit → REST API → mobile) |
| [`architecture.md`](wiki/architecture.md) | Mermaid architecture diagrams — system overview, training pipeline, model export, inference flow |
