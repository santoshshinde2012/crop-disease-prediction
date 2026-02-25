# Architecture Diagrams

Mermaid architecture diagrams for the Crop Disease Classification system.

---

## 1. System Overview

The notebook trains the model. Three consumers (Streamlit, API, Mobile) serve predictions using shared artifacts.

```mermaid
architecture-beta
    group core(server)[Shared ML Pipeline — src]
        service config(server)[config.py] in core
        service data(database)[data — loader, transforms] in core
        service models(server)[models — MobileNetV2] in core
        service trainer(server)[training — two-phase] in core
        service evaluator(server)[evaluation — metrics] in core
        service predictor(server)[inference — DiseasePredictor] in core

    group artifacts(disk)[Generated Artifacts]
        service pth(disk)[checkpoints/best_model.pth] in artifacts
        service metrics(disk)[outputs/class_names.json] in artifacts
        service tflite(disk)[exports/classifier.tflite] in artifacts

    group consumers(cloud)[Consumers]
        service notebook(server)[Jupyter Notebook] in consumers
        service streamlit(internet)[Streamlit App] in consumers
        service api(internet)[REST API] in consumers
        service mobile(server)[React Native App] in consumers

    service dataset(database)[PlantVillage Dataset]
    service export(server)[export_model.py]

    dataset:R --> L:data
    data:R --> L:trainer
    models:B --> T:trainer
    trainer:R --> L:evaluator
    evaluator{group}:R --> L:pth{group}
    evaluator{group}:B --> T:metrics{group}
    pth:R --> L:predictor{group}
    predictor:B --> T:streamlit{group}
    predictor:B --> T:api{group}
    pth:B --> T:export
    export:B --> T:tflite{group}
    tflite:R --> L:mobile
    notebook{group}:R --> L:core{group}
```

---

## 2. Training Pipeline

Phase 1 trains the classifier head (5 epochs). Phase 2 fine-tunes top 5 blocks (up to 10 epochs).

```mermaid
architecture-beta
    service dataset(database)[PlantVillage — 22K images]

    group datapipe(server)[Data Pipeline]
        service split(server)[80/20 Stratified Split] in datapipe
        service augment(server)[Augmentation — flip, rotate, zoom, jitter] in datapipe
        service normalize(server)[ImageNet Normalize] in datapipe
        service sampler(server)[Weighted Sampler] in datapipe

    group model(server)[Model]
        service backbone(server)[MobileNetV2 — ImageNet pretrained] in model
        service head(server)[Custom Head — 1280 → 128 → 15] in model

    group training(server)[Two-Phase Training]
        service phase1(server)[Phase 1 — Head only, lr=1e-3, 5 epochs] in training
        service phase2(server)[Phase 2 — Fine-tune, lr=1e-4, 10 epochs] in training

    group eval(server)[Evaluation]
        service confusion(server)[Confusion Matrix] in eval
        service report(server)[Classification Report — 97.8%] in eval
        service benchmark(server)[Inference Benchmark] in eval

    group output(disk)[Output]
        service checkpoint(disk)[best_model.pth — 9.3 MB] in output
        service metricsout(disk)[class_names.json, results.json] in output
        service plots(disk)[8 PNG Visualizations] in output

    dataset:R --> L:split
    split:R --> L:augment
    augment:R --> L:normalize
    normalize:R --> L:sampler
    sampler{group}:B --> T:backbone{group}
    backbone:B --> T:head
    head{group}:B --> T:phase1{group}
    phase1:B --> T:phase2
    phase2{group}:B --> T:confusion{group}
    confusion:R --> L:report
    report:R --> L:benchmark
    benchmark{group}:B --> T:checkpoint{group}
    checkpoint:R --> L:metricsout
    metricsout:R --> L:plots
```

---

## 3. Model Export Pipeline

Converts PyTorch model to TFLite for on-device mobile inference via ONNX intermediate format. Output goes to `exports/` and is copied to `mobile/assets/model/`.

```mermaid
architecture-beta
    service pth(disk)[checkpoints/best_model.pth]

    group step1(server)[Step 1 — PyTorch to ONNX]
        service onnx_export(server)[torch.onnx.export — opset 13] in step1
        service onnx_file(disk)[classifier.onnx — 9 MB] in step1

    group step2(server)[Step 2 — ONNX to TFLite]
        service onnx2tf(server)[onnx2tf — direct conversion] in step2
        service tflite(disk)[exports/classifier.tflite — 9 MB] in step2

    group step3(server)[Step 3 — Verify and Copy]
        service interpreter(server)[TFLite Interpreter — Verify] in step3
        service copy(disk)[Copy to mobile/assets/model/] in step3

    pth:R --> L:onnx_export
    onnx_export:R --> L:onnx_file
    onnx_file{group}:R --> L:onnx2tf{group}
    onnx2tf:R --> L:tflite
    tflite{group}:R --> L:interpreter{group}
    interpreter:R --> L:copy
```

---

## 4. Inference Flow

All consumers preprocess with ImageNet normalization (mean/std) on 224x224 input and output 15-class softmax probabilities.

```mermaid
architecture-beta
    group streamlit(cloud)[Streamlit App]
        service st_in(internet)[Upload JPG/PNG] in streamlit
        service st_pre(server)[DiseasePredictor — Resize, Normalize] in streamlit
        service st_model(server)[PyTorch — best_model.pth] in streamlit
        service st_out(internet)[Web UI — Disease Card, Treatment] in streamlit

    group api(cloud)[REST API]
        service api_in(internet)[POST /predict — multipart] in api
        service api_val(server)[Validate — type, size, integrity] in api
        service api_model(server)[PyTorch — best_model.pth] in api
        service api_out(internet)[JSON — prediction, confidence] in api

    group mobile(cloud)[Mobile App — Offline]
        service m_in(server)[Camera Capture or Gallery] in mobile
        service m_pre(server)[imageProcessor — Resize 224x224, RGBA] in mobile
        service m_model(server)[TFLite — CoreML / GPU delegate] in mobile
        service m_save(database)[AsyncStorage — Save History] in mobile
        service m_out(server)[Result Screen — Diagnosis, Treatment] in mobile

    service disease_data(database)[disease_info — symptoms, treatment, prevention]

    st_in:R --> L:st_pre
    st_pre:R --> L:st_model
    st_model:R --> L:st_out

    api_in:R --> L:api_val
    api_val:R --> L:api_model
    api_model:R --> L:api_out

    m_in:R --> L:m_pre
    m_pre:R --> L:m_model
    m_model:R --> L:m_save
    m_save:R --> L:m_out

    st_out:B --> T:disease_data
    api_out:B --> T:disease_data
    m_out:B --> T:disease_data
```
