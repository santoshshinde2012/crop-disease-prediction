# Execution Guide

End-to-end steps to run the Crop Disease Classification project.

---

## Deliverables (Assignment)

| # | Deliverable | Location |
|---|------------|----------|
| 1 | Presentation (20 min) | To be created |
| 2 | Jupyter Notebook | `notebooks/crop_disease_classification.ipynb` |
| 3 | README.md | `README.md` |
| 4 | Saved model file | `checkpoints/best_model.pth` |

---

## Step 1 — Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure Kaggle API (one-time)
# Download kaggle.json from https://www.kaggle.com/settings → "Create New Token"
mkdir -p ~/.kaggle && mv ~/Downloads/kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json

# Download PlantVillage dataset (~2 GB, ~54,000 images)
kaggle datasets download -d abdallahalidev/plantvillage-dataset
unzip -q plantvillage-dataset.zip -d plantvillage-dataset

# Create data symlink
mkdir -p data/raw
ln -sf "$(pwd)/plantvillage-dataset/plantvillage dataset/color" data/raw/color
```

---

## Step 2 — Jupyter Notebook (Parts 1–3)

This is the **primary deliverable**. Run all cells top to bottom.

```bash
cd notebooks
jupyter notebook crop_disease_classification.ipynb
```

### Part 1: Data Exploration

| Cell | Section | What It Does | Output |
|------|---------|-------------|--------|
| 0 | Intro | Markdown: objective, approach, tech stack | — |
| 1 | Setup | Import `src/` modules, detect device (MPS/CUDA/CPU), set seed | — |
| 2 | — | Markdown: Part 1 heading | — |
| 3 | 1.1 Load Dataset | `get_class_counts()` → prints 15 classes with image counts (22,115 total) | Console |
| 4 | — | Markdown: class distribution heading | — |
| 5 | 1.2 Class Distribution | `plot_class_distribution()` → bar chart, color-coded by crop | `outputs/plots/class_distribution.png` |
| 6 | — | Markdown: sample images heading | — |
| 7 | 1.3 Sample Images | `plot_sample_images()` → grid of 4 images from 5 classes | `outputs/plots/sample_images.png` |
| 8 | — | Markdown: key insights heading | — |
| 9 | 1.4 Key Insights | `print_insights()` → imbalance ratio, crop distribution, image dimensions | Console |

### Part 2: Model Building

| Cell | Section | What It Does | Output |
|------|---------|-------------|--------|
| 10 | — | Markdown: Part 2 heading | — |
| 11 | 2.1 Data Loading | `create_data_loaders()` → 80/20 train/val split with augmentation, weighted sampler | Console |
| 12 | Augmentation | `plot_augmentation_examples()` → original vs 9 augmented versions | `outputs/plots/augmentation_examples.png` |
| 13 | — | Markdown: MobileNetV2 rationale | — |
| 14 | 2.2 Build Model | `build_model()` → MobileNetV2 + custom head (2.4M params) | Console |
| 15 | — | Markdown: two-phase training explanation | — |
| 16 | 2.3 Train | `train_model()` → Phase 1: 5 epochs (head only), Phase 2: up to 10 epochs (fine-tune) | `checkpoints/best_model.pth` |
| 17 | Training Curves | `plot_training_history()` → accuracy & loss over both phases | `outputs/plots/training_history.png` |

### Part 3: Evaluation & Business Impact

| Cell | Section | What It Does | Output |
|------|---------|-------------|--------|
| 18 | — | Markdown: Part 3 heading | — |
| 19 | 3.1 Evaluate | Load best weights, `collect_predictions()`, `print_classification_report()` | Console (97.8% accuracy) |
| 20 | — | Markdown: confusion matrix heading | — |
| 21 | 3.2 Confusion Matrix | `plot_confusion_matrix()` → 15×15 heatmap | `outputs/plots/confusion_matrix.png` |
| 22 | — | Markdown: correct/incorrect heading | — |
| 23 | 3.3 Predictions | `plot_correct_incorrect()` → 5 correct + 5 incorrect with images | `outputs/plots/correct_predictions.png`, `incorrect_predictions.png` |
| 24 | — | Markdown: per-class heading | — |
| 25 | 3.4 Per-Class | `plot_per_class_accuracy()` → bar chart (green ≥90%, yellow ≥80%, red <80%) | `outputs/plots/per_class_accuracy.png` |
| 26 | — | Markdown: business recommendation heading | — |
| 27 | 3.5 Deployment Analysis | Prints model size (9.3 MB), inference time, accuracy, param count | Console |
| 28 | — | Markdown: business recommendation (MobileNetV2 vs ResNet50 vs EfficientNet comparison) | — |
| 29 | — | Markdown: save heading | — |
| 30 | 3.6 Save Results | `save_results()` → class names, metrics JSON, summary CSV | `outputs/metrics/` |
| 31 | Part 4 | Markdown: Streamlit app and REST API instructions | — |

### Generated Artifacts

```
checkpoints/best_model.pth                    # 9.3 MB PyTorch model weights
exports/crop_disease_classifier.tflite        # 9.1 MB TFLite model (from Step 5)
outputs/plots/class_distribution.png          # Class distribution bar chart
outputs/plots/sample_images.png               # Sample images grid
outputs/plots/augmentation_examples.png       # Augmentation examples
outputs/plots/training_history.png            # Training curves
outputs/plots/confusion_matrix.png            # 15×15 confusion matrix
outputs/plots/correct_predictions.png         # Top 5 correct predictions
outputs/plots/incorrect_predictions.png       # Top 5 incorrect predictions
outputs/plots/per_class_accuracy.png          # Per-class accuracy bar chart
outputs/metrics/class_names.json              # 15 class labels
outputs/metrics/results.json                  # Full classification report
outputs/metrics/classification_summary.csv    # Summary table
```

### Runtime

| Hardware | Time |
|----------|------|
| Apple MPS (M-series) | ~10–15 min |
| NVIDIA CUDA | ~10–15 min |
| CPU | ~30–45 min |

---

## Step 3 — Streamlit App (Part 4 Bonus)

> Requires: `checkpoints/best_model.pth` and `outputs/metrics/class_names.json` from Step 2.

```bash
streamlit run streamlit_app/app.py
# Open http://localhost:8501
```

| Page | Description |
|------|-------------|
| **Diagnosis** | Upload a leaf image → disease name, confidence %, severity, treatment, prevention |
| **Model Performance** | Accuracy metrics, confusion matrix, training history, per-class performance |
| **Disease Library** | Browse 15 diseases with crop filter tabs, symptoms, treatment |

Stop: `Ctrl+C`

---

## Step 4 — REST API

> Requires: `checkpoints/best_model.pth` and `outputs/metrics/class_names.json` from Step 2.

```bash
uvicorn api.main:app --reload
# Swagger UI: http://localhost:8000/docs
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check with model status |
| `POST` | `/api/v1/predict` | Upload leaf image → prediction JSON |
| `GET` | `/api/v1/diseases` | List all 15 diseases (optional `?crop=` filter) |
| `GET` | `/api/v1/diseases/{name}` | Single disease detail |

```bash
# Test
curl http://localhost:8000/api/v1/health
curl -X POST http://localhost:8000/api/v1/predict -F "file=@path/to/leaf.jpg"
```

Stop: `Ctrl+C`

---

## Step 5 — Export TFLite Model (Mobile)

> Requires: `checkpoints/best_model.pth` from Step 2.

```bash
# Install export dependencies (torch already installed from requirements.txt)
pip install onnx==1.16.2 onnx2tf tensorflow

# Export: PyTorch → ONNX → TFLite (via onnx2tf)
python scripts/export_model.py
# Output: exports/crop_disease_classifier.tflite (~9 MB)
#         + copied to mobile/assets/model/ for Metro bundling
```

Optional — sync mobile asset data if class names or disease info changed:

```bash
python scripts/sync_mobile_assets.py
```

---

## Step 6 — Mobile App (React Native)

> Requires: `exports/crop_disease_classifier.tflite` from Step 5 (auto-copied to `mobile/assets/model/`).

```bash
cd mobile
npm install

# iOS
cd ios && pod install && cd ..
npm run ios                  # or: npm start (Terminal 1) + npm run ios:no-packager (Terminal 2)

# Android
npx react-native run-android
```

| Screen | What It Does |
|--------|-------------|
| **Home** | Hero with model stats, "Scan a Leaf" button |
| **Camera** | Capture leaf photo or pick from gallery |
| **Result** | Disease name, confidence %, severity, treatment, prevention |
| **History** | Past scans saved locally (offline) |
| **Library** | Browse 15 diseases with crop filter tabs |

---

## Step 7 — E2E Testing (Optional)

> Requires: Built app from Step 6 and [Maestro CLI](https://maestro.mobile.dev/getting-started/installation).

```bash
curl -Ls "https://get.maestro.mobile.dev" | bash
cd mobile
maestro test .maestro/flows/
# iOS: maestro test -e appId=org.reactjs.native.example.CropDiseaseApp .maestro/flows/
```

---

## Quick Reference

```
1. pip install -r requirements.txt             # Python deps
2. kaggle datasets download ...                # Dataset (~2 GB)
3. mkdir -p data/raw && ln -sf ...             # Data symlink
4. jupyter notebook notebooks/...              # Notebook (Parts 1–3)
5. streamlit run streamlit_app/app.py          # Streamlit (Part 4)
6. uvicorn api.main:app --reload               # REST API
7. pip install onnx==1.16.2 onnx2tf tensorflow  # Export deps
8. python scripts/export_model.py              # TFLite model
9. cd mobile && npm install                    # Mobile deps
10. cd ios && pod install && cd .. && npm run ios  # Run app
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `FileNotFoundError: data/raw/color/` | Run symlink: `ln -sf "$(pwd)/plantvillage-dataset/plantvillage dataset/color" data/raw/color` |
| `FileNotFoundError: checkpoints/best_model.pth` | Run the notebook first (Step 2) |
| `ModuleNotFoundError: onnx2tf` | `pip install onnx==1.16.2 onnx2tf tensorflow` |
| Model not found in mobile app | Run `python scripts/export_model.py` (Step 5) |
| "No script URL provided" in simulator | Run `npm start` in a separate terminal, then reload (Cmd+R) |
| Pod install fails | `cd mobile/ios && pod deintegrate && pod install --repo-update` |
| Metro cache issues | `npx react-native start --reset-cache` |
