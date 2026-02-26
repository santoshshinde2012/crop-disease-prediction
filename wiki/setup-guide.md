# Setup Guide — Crop Disease Classification

Complete prerequisites and setup instructions for running all project components: Jupyter notebooks, FastAPI server, Streamlit app, React Native mobile app, TFLite export, Docker deployment, and WhatsApp integration.

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start (Automated)](#quick-start-automated)
- [Manual Setup](#manual-setup)
  - [1. Python Environment](#1-python-environment)
  - [2. Dataset](#2-dataset)
  - [3. Jupyter Notebook](#3-jupyter-notebook)
  - [4. Streamlit App](#4-streamlit-app)
  - [5. REST API (FastAPI)](#5-rest-api-fastapi)
  - [6. TFLite Model Export](#6-tflite-model-export)
  - [7. React Native Mobile App](#7-react-native-mobile-app)
  - [8. Docker Deployment](#8-docker-deployment)
  - [9. WhatsApp Integration (Twilio)](#9-whatsapp-integration-twilio)
- [Inference Modes](#inference-modes)
- [Environment Variables](#environment-variables)
- [Platform-Specific Notes](#platform-specific-notes)
- [Verification Checklist](#verification-checklist)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Required

| Tool | Minimum Version | Purpose | Install |
|------|----------------|---------|---------|
| **Python** | 3.10+ | ML pipeline, API, Streamlit | [python.org](https://www.python.org/downloads/) or `brew install python@3.11` |
| **pip** | 22+ | Python package management | Included with Python |
| **Git** | 2.30+ | Version control | [git-scm.com](https://git-scm.com/downloads) |

### Required for Mobile App

| Tool | Minimum Version | Purpose | Install |
|------|----------------|---------|---------|
| **Node.js** | 18+ | React Native CLI and Metro bundler | [nodejs.org](https://nodejs.org/) or `brew install node@20` |
| **npm** | 9+ | JavaScript package management | Included with Node.js |
| **Xcode** | 15+ | iOS builds (macOS only) | Mac App Store |
| **CocoaPods** | 1.14+ | iOS native dependency management | `sudo gem install cocoapods` |
| **Java JDK** | 17+ | Android builds | `brew install openjdk@17` or [adoptium.net](https://adoptium.net/) |
| **Android Studio** | Latest | Android SDK, emulator | [developer.android.com](https://developer.android.com/studio) |

### Optional

| Tool | Purpose | Install |
|------|---------|---------|
| **Docker** | Containerized API deployment | [docker.com](https://docs.docker.com/get-docker/) |
| **Kaggle CLI** | Automated dataset download | `pip install kaggle` |
| **ngrok** | WhatsApp webhook tunneling (local dev) | [ngrok.com](https://ngrok.com/download) or `brew install ngrok` |

### Hardware Recommendations

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 8 GB | 16 GB |
| **Disk** | 10 GB free | 20 GB free (with dataset) |
| **GPU** | None (CPU works) | Apple MPS / NVIDIA CUDA (10x faster training) |

Training runtime:
- **Apple MPS / NVIDIA CUDA**: ~10–15 min
- **CPU only**: ~30–45 min

---

## Quick Start (Automated)

The setup script handles all prerequisites automatically:

```bash
# Make executable (one-time)
chmod +x scripts/setup.sh

# Full interactive setup
./scripts/setup.sh

# Or non-interactive full setup
./scripts/setup.sh --all
```

### Targeted Setup

```bash
./scripts/setup.sh --python    # Python environment only
./scripts/setup.sh --dataset   # Download PlantVillage dataset
./scripts/setup.sh --export    # TFLite export dependencies
./scripts/setup.sh --mobile    # React Native dependencies
./scripts/setup.sh --docker    # Build Docker image
./scripts/setup.sh --verify    # Check what's installed
```

---

## Manual Setup

### 1. Python Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows (PowerShell)

# Upgrade pip
pip install --upgrade pip

# Install all Python dependencies
pip install -r requirements.txt
```

**What gets installed** (from `requirements.txt`):

| Package | Version | Purpose |
|---------|---------|---------|
| `torch` | >=2.0 | Deep learning framework |
| `torchvision` | >=0.15 | Image transforms, MobileNetV2 |
| `matplotlib` | >=3.7 | Static plots |
| `seaborn` | >=0.13 | Statistical visualization |
| `scikit-learn` | >=1.3 | Metrics, class weights, train/val split |
| `pandas` | >=2.0 | Data manipulation |
| `streamlit` | >=1.36 | Web UI framework |
| `plotly` | >=5.18 | Interactive charts |
| `requests` | >=2.28 | HTTP client |
| `Pillow` | >=10.0 | Image I/O |
| `fastapi` | >=0.115 | REST API framework |
| `uvicorn[standard]` | >=0.30 | ASGI server |
| `gunicorn` | >=22.0 | Production WSGI/ASGI server |
| `python-multipart` | >=0.0.9 | File upload parsing |
| `python-dotenv` | >=1.0 | Environment variable loading |
| `jupyter` | latest | Notebook runtime |
| `tflite-runtime` | >=2.14 | TFLite inference (Streamlit offline) |
| `twilio` | >=9.0 | WhatsApp integration |
| `httpx` | >=0.27 | Async HTTP client |

---

### 2. Dataset

The project uses the [PlantVillage dataset](https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset) (~2 GB, ~54,000 images across 38 classes). The project filters to 15 classes (3 crops: Tomato, Potato, Corn) totaling 22,115 images.

#### Option A: Kaggle CLI (recommended)

```bash
# Install Kaggle CLI (if not already)
pip install kaggle

# Setup credentials (one-time)
# 1. Go to https://www.kaggle.com/settings → "Create New Token"
# 2. Download kaggle.json
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Download and extract
kaggle datasets download -d abdallahalidev/plantvillage-dataset
unzip -q plantvillage-dataset.zip -d plantvillage-dataset
rm plantvillage-dataset.zip

# Create data symlink
mkdir -p data/raw
ln -sf "$(pwd)/plantvillage-dataset/plantvillage dataset/color" data/raw/color
```

#### Option B: Manual Download

1. Go to https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset
2. Click "Download" (requires Kaggle account)
3. Extract to `plantvillage-dataset/` in the project root
4. Create the symlink:

```bash
mkdir -p data/raw
ln -sf "$(pwd)/plantvillage-dataset/plantvillage dataset/color" data/raw/color
```

#### Verify

```bash
ls data/raw/color/ | head -5
# Should show disease folders like:
# Corn_(maize)___Common_rust_
# Corn_(maize)___Gray_leaf_spot
# ...
```

---

### 3. Jupyter Notebook

> **Prerequisite**: Python environment (Step 1), dataset (Step 2)

```bash
source .venv/bin/activate
jupyter notebook notebooks/crop_disease_classification.ipynb
```

Run all cells top to bottom. The notebook has 3 parts:

| Part | What It Does | Key Output |
|------|-------------|------------|
| **Part 1** — Data Exploration | Class distribution, sample images, insights | Plots in `outputs/plots/` |
| **Part 2** — Model Building | MobileNetV2 two-phase training (5+10 epochs) | `checkpoints/best_model.pth` (9.3 MB) |
| **Part 3** — Evaluation | Confusion matrix, per-class accuracy, metrics | `outputs/metrics/results.json`, `class_names.json` |

The notebook generates these files required by other components:
- `checkpoints/best_model.pth` — Trained model weights (required by API, Streamlit, export)
- `outputs/metrics/class_names.json` — Class label mapping (required by API, Streamlit)
- `outputs/metrics/results.json` — Metrics (used by Streamlit dashboard)

---

### 4. Streamlit App

> **Prerequisite**: Trained model from notebook (`checkpoints/best_model.pth`, `outputs/metrics/class_names.json`)

```bash
source .venv/bin/activate
streamlit run streamlit_app/app.py
# Opens at http://localhost:8501
```

| Page | Description |
|------|-------------|
| **Diagnosis** | Upload leaf image → disease prediction with 3 inference modes |
| **Dashboard** | Model performance metrics, confusion matrix, per-class accuracy |
| **Disease Library** | Browse all 15 diseases by crop with symptoms and treatment |

The Diagnosis page supports 3 inference modes (toggleable):
- **Local Model** (PyTorch) — Direct model inference on CPU/GPU
- **TFLite** — Uses `tflite-runtime` for lightweight inference
- **Online API** — Sends image to REST API (requires Step 5 API running)

---

### 5. REST API (FastAPI)

> **Prerequisite**: Trained model from notebook (`checkpoints/best_model.pth`, `outputs/metrics/class_names.json`)

```bash
source .venv/bin/activate

# Development (with auto-reload)
uvicorn api.main:app --reload --port 8000

# Production
gunicorn api.main:app -k uvicorn.workers.UvicornWorker --workers 2 --bind 0.0.0.0:8000
```

**Endpoints**:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check with model status |
| `GET` | `/api/v1/health/live` | Liveness probe |
| `POST` | `/api/v1/predict` | Upload leaf image → prediction JSON |
| `GET` | `/api/v1/diseases` | List all 15 diseases (optional `?crop=` filter) |
| `GET` | `/api/v1/diseases/{name}` | Disease detail by name |
| `POST` | `/api/v1/whatsapp/webhook` | Twilio WhatsApp webhook |

**Interactive docs**: http://localhost:8000/docs (Swagger UI)

**Test commands**:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Predict
curl -X POST http://localhost:8000/api/v1/predict -F "file=@path/to/leaf.jpg"

# List diseases
curl http://localhost:8000/api/v1/diseases

# Filter by crop
curl "http://localhost:8000/api/v1/diseases?crop=tomato"
```

---

### 6. TFLite Model Export

> **Prerequisite**: Trained model (`checkpoints/best_model.pth`)

The mobile app uses TensorFlow Lite for on-device inference. The conversion pipeline is:

```
PyTorch (.pth) → ONNX → TFLite (via onnx2tf)
```

```bash
source .venv/bin/activate

# Install export-specific dependencies
pip install onnx==1.16.2 onnx2tf tensorflow

# Run export
python scripts/export_model.py
```

**Output**:
- `exports/crop_disease_classifier.tflite` (9.1 MB) — Canonical export
- `mobile/assets/model/crop_disease_classifier.tflite` — Auto-copied for Metro bundling

**Optional**: Sync class names and disease info to mobile assets:

```bash
python scripts/sync_mobile_assets.py
```

---

### 7. React Native Mobile App

> **Prerequisites**:
> - Node.js >= 18
> - TFLite model exported (Step 6) — or existing `mobile/assets/model/crop_disease_classifier.tflite`
> - Xcode (for iOS) or Android Studio (for Android)

```bash
cd mobile

# Install JavaScript dependencies
npm install

# iOS (macOS only)
cd ios && pod install && cd ..
npm run ios

# Android
npm run android

# Start Metro bundler only (if building separately)
npm start
```

**App screens**:

| Screen | Description |
|--------|-------------|
| **Home** | Hero banner, feature cards, online/offline toggle, "Scan a Leaf" button |
| **Camera** | Camera capture with leaf guide overlay, gallery picker, demo image (simulator) |
| **Result** | Diagnosis card, severity, confidence, treatment, symptoms, prevention, top-5 chart |
| **History** | Past predictions (stored locally, max 50 entries) |
| **Library** | Browse 15 diseases filtered by crop |

**Inference modes** (toggle in Home/Camera screens):
- **Offline** (default): TFLite on-device inference — no server needed
- **Online**: Sends image to REST API at `localhost:8000`

**API URL configuration** (for online mode):
- Android emulator: `http://10.0.2.2:8000` (auto-configured)
- iOS simulator: `http://localhost:8000` (auto-configured)
- Physical device: Edit `InferenceModeContext.tsx` with your machine's IP

---

### 8. Docker Deployment

> **Prerequisite**: Docker installed, trained model (`checkpoints/best_model.pth`)

```bash
# Build and start
docker compose up --build

# Run in background
docker compose up --build -d

# Stop
docker compose down
```

The Docker setup:
- Multi-stage build (Python 3.11-slim)
- Mounts `checkpoints/`, `exports/`, `outputs/metrics/` as read-only volumes
- Exposes port `8000`
- Health check: `GET /api/v1/health/live`
- Memory limit: 2 GB
- Runs as non-root user

Access: http://localhost:8000/docs

---

### 9. WhatsApp Integration (Twilio)

> **Prerequisites**: REST API running (Step 5), Twilio account

See [whatsapp-integration.md](whatsapp-integration.md) for the complete guide.

**Quick setup**:

```bash
# 1. Create .env from template
cp .env.example .env

# 2. Edit .env with your Twilio credentials:
#    TWILIO_ACCOUNT_SID=ACxxxxx
#    TWILIO_AUTH_TOKEN=xxxxx
#    WHATSAPP_ENABLE_SIGNATURE_VALIDATION=false  (for local dev)

# 3. Start the API
uvicorn api.main:app --reload --port 8000

# 4. Tunnel with ngrok (separate terminal)
ngrok http 8000

# 5. Configure Twilio Sandbox:
#    - Go to https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
#    - Set webhook URL: https://<ngrok-id>.ngrok.io/api/v1/whatsapp/webhook
#    - Method: POST
```

**Supported messages**:

| Message | Response |
|---------|----------|
| `hi`, `hello` | Welcome message with instructions |
| `help`, `?` | Available commands and photo tips |
| `crops`, `diseases` | Supported crops and disease counts |
| Leaf photo (JPEG/PNG) | Full diagnosis with treatment and prevention |

---

## Inference Modes

The project supports three inference backends, available across different components:

| Mode | Backend | Latency | Where Available |
|------|---------|---------|-----------------|
| **Local (PyTorch)** | MobileNetV2 on CPU/MPS/CUDA | ~8 ms (GPU), ~50 ms (CPU) | Streamlit, API |
| **TFLite** | TensorFlow Lite runtime | <100 ms on-device | Streamlit, Mobile app |
| **Online (REST API)** | FastAPI + PyTorch | ~100–200 ms (network) | Streamlit, Mobile app, WhatsApp |

### Model details

| Property | Value |
|----------|-------|
| Architecture | MobileNetV2 + custom classifier head |
| Input | 224 x 224 x 3 RGB (ImageNet normalized) |
| Output | 15 class logits |
| Parameters | 2,389,775 |
| Model size | 9.3 MB (PyTorch) / 9.1 MB (TFLite) |
| Accuracy | 97.83% on validation set |

### Normalization constants (ImageNet)

```
Mean: [0.485, 0.456, 0.406]
Std:  [0.229, 0.224, 0.225]
```

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `CORS_ORIGINS` | `*` | No | Comma-separated allowed CORS origins |
| `PREDICT_RATE_LIMIT_PER_MINUTE` | `30` | No | Max predictions per IP per minute |
| `TWILIO_ACCOUNT_SID` | — | WhatsApp only | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | — | WhatsApp only | Twilio Auth Token |
| `TWILIO_WHATSAPP_NUMBER` | `whatsapp:+14155238886` | WhatsApp only | Twilio sandbox number |
| `TWILIO_WEBHOOK_URL` | — | No | Override webhook URL (behind proxy) |
| `WHATSAPP_LOW_CONFIDENCE_THRESHOLD` | `0.60` | No | Below this, warn user about low confidence |
| `WHATSAPP_RATE_LIMIT_PER_MINUTE` | `10` | No | Max requests per phone number per minute |
| `WHATSAPP_IMAGE_DOWNLOAD_TIMEOUT` | `10` | No | Image download timeout (seconds) |
| `WHATSAPP_ENABLE_SIGNATURE_VALIDATION` | `true` | No | Set `false` for local dev with ngrok |

---

## Platform-Specific Notes

### macOS (Apple Silicon — M1/M2/M3/M4)

- PyTorch uses **MPS** (Metal Performance Shaders) for GPU acceleration
- Training is ~10–15 min with MPS
- TFLite mobile uses **CoreML** delegate on iOS for Neural Engine acceleration
- Install Xcode from App Store for iOS development
- CocoaPods: `sudo gem install cocoapods`

### macOS (Intel)

- PyTorch uses CPU (no MPS)
- All other features work identically

### Linux (with NVIDIA GPU)

- Install CUDA toolkit for GPU acceleration: https://developer.nvidia.com/cuda-toolkit
- PyTorch automatically detects CUDA
- Training is ~10–15 min with CUDA
- `tflite-runtime` may need specific wheel for your platform

### Linux (CPU only)

- Training takes ~30–45 min
- All inference modes work but are slower
- For Docker deployment, no special GPU configuration needed

### Windows

- Use WSL2 (Windows Subsystem for Linux) for best compatibility
- Python and Node.js install natively
- Mobile development requires Android Studio (iOS not available on Windows)
- Docker Desktop works with WSL2 backend

---

## Verification Checklist

Run the automated verification:

```bash
./scripts/setup.sh --verify
```

Or check manually:

```
[ ] Python 3.10+ installed
[ ] Virtual environment created (.venv/)
[ ] requirements.txt installed
[ ] Dataset downloaded (data/raw/color/ — 38+ class folders)
[ ] Notebook executed successfully
[ ] Trained model exists (checkpoints/best_model.pth — ~9.3 MB)
[ ] Metrics generated (outputs/metrics/class_names.json, results.json)
[ ] Streamlit app runs (http://localhost:8501)
[ ] REST API runs (http://localhost:8000/docs)
[ ] TFLite exported (exports/crop_disease_classifier.tflite — ~9.1 MB)
[ ] Mobile model copied (mobile/assets/model/crop_disease_classifier.tflite)
[ ] Node.js 18+ installed
[ ] npm install completed (mobile/node_modules/)
[ ] iOS Pods installed (mobile/ios/Pods/) [macOS only]
[ ] Mobile app builds and runs
[ ] .env configured (for WhatsApp)
[ ] Docker image builds (optional)
```

---

## Troubleshooting

### Python / General

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'src'` | Run from the project root directory, not from a subdirectory |
| `FileNotFoundError: data/raw/color/` | Create symlink: `ln -sf "$(pwd)/plantvillage-dataset/plantvillage dataset/color" data/raw/color` |
| `FileNotFoundError: checkpoints/best_model.pth` | Run the Jupyter notebook first (Step 3) |
| `tflite-runtime` install fails | Try: `pip install tflite-runtime` — or for specific platform: check [TFLite guide](https://www.tensorflow.org/lite/guide/python) |
| PyTorch MPS error on macOS | Update to macOS 12.3+ and PyTorch 2.0+ |
| CUDA out of memory | Reduce `BATCH_SIZE` in `src/config.py` (default: 32) |

### Streamlit

| Problem | Solution |
|---------|----------|
| Streamlit won't start | Check port 8501 is free: `lsof -i :8501` |
| "Model not found" in Streamlit | Ensure `checkpoints/best_model.pth` and `outputs/metrics/class_names.json` exist |
| Online mode fails | Start the REST API: `uvicorn api.main:app --reload` |

### REST API

| Problem | Solution |
|---------|----------|
| Port 8000 in use | `uvicorn api.main:app --reload --port 8001` |
| "Model loading failed" at startup | Check `checkpoints/best_model.pth` exists |
| CORS errors from frontend | Set `CORS_ORIGINS=*` in `.env` |

### TFLite Export

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: onnx2tf` | `pip install onnx==1.16.2 onnx2tf tensorflow` |
| onnx2tf conversion fails | Ensure `onnx==1.16.2` (specific version required for compatibility) |
| "No .tflite file found" | Check onnx2tf output — may need `tensorflow>=2.14` |

### Mobile App

| Problem | Solution |
|---------|----------|
| `npm install` fails | Delete `node_modules/` and `package-lock.json`, try again |
| "No script URL provided" (iOS) | Run `npm start` in a separate terminal, then Cmd+R to reload |
| Pod install fails | `cd mobile/ios && pod deintegrate && pod install --repo-update` |
| Metro cache issues | `npx react-native start --reset-cache` |
| TFLite model not loading | Run `python scripts/export_model.py` to regenerate and copy |
| Android build fails | Ensure `JAVA_HOME` points to JDK 17+, Android SDK installed |
| Camera not working (simulator) | Use gallery picker or demo image — simulators have no camera |
| Online mode: "API Unavailable" | Start API: `uvicorn api.main:app --reload`; for physical device, use machine IP |

### WhatsApp

| Problem | Solution |
|---------|----------|
| "Invalid Twilio signature" | Set `WHATSAPP_ENABLE_SIGNATURE_VALIDATION=false` in `.env` for local dev |
| No WhatsApp response | Check ngrok is running and webhook URL is correct in Twilio Console |
| Image analysis fails | Ensure the API can download images (check network/firewall) |
| Rate limited | Default: 10 req/min per phone. Adjust `WHATSAPP_RATE_LIMIT_PER_MINUTE` |

### Docker

| Problem | Solution |
|---------|----------|
| Build fails | Ensure `checkpoints/`, `exports/`, `outputs/metrics/` have the required files |
| Container OOM killed | Increase `deploy.resources.limits.memory` in `docker-compose.yml` (default: 2G) |
| Health check failing | Wait 60s for startup; check logs: `docker compose logs api` |

---

## Dependency Pipeline

This diagram shows the order of operations and what each component depends on:

```
┌─────────────────────────────────────────────────────────────┐
│                     1. SETUP                                │
│  Python 3.10+ → pip install -r requirements.txt             │
│  Kaggle CLI → download dataset → symlink data/raw/color     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 2. JUPYTER NOTEBOOK                          │
│  Train model → checkpoints/best_model.pth                   │
│  Generate metrics → outputs/metrics/class_names.json        │
│                     outputs/metrics/results.json            │
└──────┬──────────────────┬───────────────────┬───────────────┘
       │                  │                   │
       ▼                  ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐
│ 3. STREAMLIT │  │  4. REST API │  │ 5. TFLITE EXPORT    │
│ (web UI)     │  │  (FastAPI)   │  │ pip install onnx    │
│ Port 8501    │  │  Port 8000   │  │   onnx2tf tensorflow│
│              │  │              │  │ export_model.py     │
│ Modes:       │  │ Used by:     │  │  → exports/*.tflite │
│ - Local      │  │ - Streamlit  │  │  → mobile/assets/   │
│ - TFLite     │  │ - Mobile     │  └──────────┬──────────┘
│ - Online ────┼──┤ - WhatsApp   │             │
└──────────────┘  └──────┬───────┘             ▼
                         │            ┌─────────────────────┐
                         │            │ 6. MOBILE APP       │
                         │            │ npm install          │
                         │            │ pod install (iOS)    │
                         │            │                     │
                         │            │ Modes:              │
                         │            │ - Offline (TFLite)  │
                         └────────────┤ - Online (REST API) │
                                      └─────────────────────┘
                         │
                         ▼
               ┌─────────────────────┐
               │ 7. WHATSAPP BOT     │
               │ .env (Twilio creds) │
               │ ngrok (local dev)   │
               └─────────────────────┘
```

---

## File Inventory

Key files generated/required at each stage:

| File | Generated By | Required By |
|------|-------------|-------------|
| `data/raw/color/` | Dataset download | Notebook |
| `checkpoints/best_model.pth` | Notebook | API, Streamlit, TFLite export |
| `outputs/metrics/class_names.json` | Notebook | API, Streamlit |
| `outputs/metrics/results.json` | Notebook | Streamlit dashboard |
| `outputs/plots/*.png` | Notebook | Streamlit dashboard |
| `exports/crop_disease_classifier.tflite` | `export_model.py` | Streamlit (TFLite mode) |
| `mobile/assets/model/crop_disease_classifier.tflite` | `export_model.py` | Mobile app |
| `mobile/assets/data/class_names.json` | `sync_mobile_assets.py` | Mobile app |
| `mobile/assets/data/disease_info.json` | `sync_mobile_assets.py` | Mobile app |
| `.env` | Manual (from `.env.example`) | WhatsApp integration |
