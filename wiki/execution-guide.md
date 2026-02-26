# Execution Guide

Run the project components in order. Each step builds on the previous one.

```
Setup → Notebook → Streamlit → REST API → TFLite Export → Mobile App → WhatsApp Bot
                   (optional)   (optional)   (optional)     (optional)   (optional)
```

> Only **Setup** and **Notebook** are required for the assignment. Everything after is optional.

---

## Step 1 — Setup

```bash
pip install -r requirements.txt

# Kaggle API (one-time): download kaggle.json from https://www.kaggle.com/settings
mkdir -p ~/.kaggle && mv ~/Downloads/kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json

# Download dataset (~2 GB)
kaggle datasets download -d abdallahalidev/plantvillage-dataset
unzip -q plantvillage-dataset.zip -d plantvillage-dataset

# Create data symlink
mkdir -p data/raw
ln -sf "$(pwd)/plantvillage-dataset/plantvillage dataset/color" data/raw/color
```

---

## Step 2 — Jupyter Notebook

> **Primary deliverable.** Run all cells top to bottom.

```bash
cd notebooks && jupyter notebook crop_disease_classification.ipynb
```

| Part | What happens | Key output |
|------|-------------|------------|
| **Part 1** | Data exploration — class distribution, sample images, 3 insights | `outputs/plots/class_distribution.png`, `sample_images.png` |
| **Part 2** | Model building — augmentation, MobileNetV2, two-phase training | `checkpoints/best_model.pth` |
| **Part 3** | Evaluation — confusion matrix, correct/incorrect predictions, business recommendation | `outputs/plots/confusion_matrix.png`, `outputs/metrics/results.json` |

**Runtime:** ~10-15 min (GPU) / ~30-45 min (CPU)

<details>
<summary>Generated artifacts</summary>

```
checkpoints/best_model.pth                 # 9.3 MB model weights
outputs/plots/class_distribution.png       # Class distribution bar chart
outputs/plots/sample_images.png            # Sample images grid
outputs/plots/augmentation_examples.png    # Augmentation examples
outputs/plots/training_history.png         # Training curves
outputs/plots/confusion_matrix.png         # 15x15 confusion matrix
outputs/plots/correct_predictions.png      # Top 5 correct predictions
outputs/plots/incorrect_predictions.png    # Top 5 incorrect predictions
outputs/plots/per_class_accuracy.png       # Per-class accuracy bar chart
outputs/metrics/class_names.json           # 15 class labels
outputs/metrics/results.json               # Full classification report
outputs/metrics/classification_summary.csv # Summary table
```

</details>

---

## Step 3 — Streamlit App

> Requires: `checkpoints/best_model.pth` and `outputs/metrics/class_names.json` from Step 2.

```bash
streamlit run streamlit_app/app.py
# Open http://localhost:8501
```

Three pages: Diagnosis, Model Performance, Disease Library. Stop with `Ctrl+C`.

---

## Step 4 — REST API

> Requires: `checkpoints/best_model.pth` and `outputs/metrics/class_names.json` from Step 2.

```bash
uvicorn api.main:app --reload
# Swagger docs: http://localhost:8000/docs
```

Test: `curl -X POST http://localhost:8000/api/v1/predict -F "file=@path/to/leaf.jpg"`

Stop with `Ctrl+C`.

---

## Step 5 — TFLite Export

> Requires: `checkpoints/best_model.pth` from Step 2.

```bash
pip install onnx==1.16.2 onnx2tf tensorflow
python scripts/export_model.py
# Output: exports/crop_disease_classifier.tflite (auto-copied to mobile/assets/model/)
```

---

## Step 6 — Mobile App

> Requires: TFLite model from Step 5.

```bash
cd mobile && npm install
cd ios && pod install && cd ..
npx react-native run-ios        # or: npx react-native run-android
```

---

## Step 7 — WhatsApp Bot

> Requires: REST API running (Step 4) + [Twilio account](https://www.twilio.com/try-twilio).

```bash
cp .env.example .env             # fill in TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
uvicorn api.main:app --reload    # start API (if not already running)
ngrok http 8000                  # in a separate terminal — copy HTTPS URL to Twilio Console
```

Set `WHATSAPP_ENABLE_SIGNATURE_VALIDATION=false` in `.env` for local dev.

Full guide: [whatsapp-integration.md](whatsapp-integration.md)

---

## Quick Reference

```
1. pip install -r requirements.txt
2. kaggle datasets download -d abdallahalidev/plantvillage-dataset
3. mkdir -p data/raw && ln -sf "$(pwd)/plantvillage-dataset/plantvillage dataset/color" data/raw/color
4. cd notebooks && jupyter notebook crop_disease_classification.ipynb
5. streamlit run streamlit_app/app.py
6. uvicorn api.main:app --reload
7. pip install onnx==1.16.2 onnx2tf tensorflow && python scripts/export_model.py
8. cd mobile && npm install && cd ios && pod install && cd .. && npx react-native run-ios
9. cp .env.example .env && ngrok http 8000
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
| "Invalid Twilio signature" in dev | Set `WHATSAPP_ENABLE_SIGNATURE_VALIDATION=false` in `.env` |
| No WhatsApp response | Check ngrok is running and API shows incoming POST in logs |
