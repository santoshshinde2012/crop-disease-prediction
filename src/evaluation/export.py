"""Export evaluation results: JSON, CSV, class names."""
import os
import json

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report

from src.config import MODEL_PATH, METRICS_DIR
from src.evaluation.benchmark import benchmark_inference


def save_results(accuracy, model, class_names, history, per_class_acc,
                 total_params, total_images, best_val_acc, y_true, y_pred, device):
    """Save class_names.json, results.json, and model_performance_summary.csv."""
    # Class names
    with open(METRICS_DIR / "class_names.json", "w") as f:
        json.dump(class_names, f, indent=2)

    # Inference benchmark
    avg_ms = benchmark_inference(model, device)
    model_size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)

    print(f"\nMODEL DEPLOYMENT ANALYSIS")
    print(f"  Architecture:     MobileNetV2 + Custom Head")
    print(f"  Model Size:       {model_size_mb:.1f} MB")
    print(f"  Total Params:     {total_params:,}")
    print(f"  Avg Inference:    {avg_ms:.1f} ms/image")
    print(f"  Val Accuracy:     {accuracy:.4f}")

    # Results JSON
    num_classes = len(class_names)
    results = {
        "accuracy": float(accuracy),
        "model_size_mb": float(model_size_mb),
        "avg_inference_ms": float(avg_ms),
        "total_params": total_params,
        "num_classes": num_classes,
        "total_images": total_images,
        "best_val_acc": float(best_val_acc),
        "class_names": class_names,
        "history": history,
        "per_class_accuracy": {class_names[i]: float(per_class_acc[i]) for i in range(num_classes)},
    }
    with open(METRICS_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Performance summary CSV
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
    rows = []
    for cls_name in class_names:
        r = report[cls_name]
        rows.append({
            "Class": cls_name,
            "Precision": f"{r['precision']:.3f}",
            "Recall": f"{r['recall']:.3f}",
            "F1-Score": f"{r['f1-score']:.3f}",
            "Support": int(r["support"]),
        })
    rows.append({
        "Class": "OVERALL (weighted avg)",
        "Precision": f"{report['weighted avg']['precision']:.3f}",
        "Recall": f"{report['weighted avg']['recall']:.3f}",
        "F1-Score": f"{report['weighted avg']['f1-score']:.3f}",
        "Support": int(report["weighted avg"]["support"]),
    })
    pd.DataFrame(rows).to_csv(METRICS_DIR / "model_performance_summary.csv", index=False)

    print(f"Saved: class_names.json, results.json, model_performance_summary.csv")
