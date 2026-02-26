"""Dashboard page: model performance metrics and evaluation plots."""
import json

import pandas as pd
import streamlit as st

from src.config import PLOTS_DIR, RESULTS_PATH
from components import page_header, section_header, divider, metric_card


@st.cache_data
def _load_results():
    with open(RESULTS_PATH) as f:
        return json.load(f)


def show():
    page_header(
        "Model Performance",
        "MobileNetV2 evaluation metrics and analysis on the PlantVillage dataset.",
    )

    results = _load_results()

    # ── Metric cards ──
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    metric_card("Validation Accuracy", f"{results['accuracy']:.1%}", col=c1)
    metric_card("Model Size", f"{results['model_size_mb']:.1f} MB", col=c2)
    metric_card("Inference Speed", f"{results['avg_inference_ms']:.1f} ms", col=c3)
    metric_card("Disease Classes", str(results["num_classes"]), col=c4)

    divider()

    # ── Training history ──
    section_header("Training History")
    st.image(str(PLOTS_DIR / "training_history.png"), use_column_width=True)

    divider()

    # ── Confusion matrix & Per-class accuracy side by side ──
    col_cm, col_pca = st.columns(2, gap="medium")
    with col_cm:
        section_header("Confusion Matrix")
        st.image(str(PLOTS_DIR / "confusion_matrix.png"), use_column_width=True)
    with col_pca:
        section_header("Per-Class Accuracy")
        st.image(str(PLOTS_DIR / "per_class_accuracy.png"), use_column_width=True)

    divider()

    # ── Sample predictions ──
    section_header("Sample Predictions")
    tab_correct, tab_incorrect = st.tabs(["Correct Predictions", "Incorrect Predictions"])
    with tab_correct:
        st.image(str(PLOTS_DIR / "correct_predictions.png"), use_column_width=True)
    with tab_incorrect:
        st.image(str(PLOTS_DIR / "incorrect_predictions.png"), use_column_width=True)

    divider()

    # ── Per-class accuracy table ──
    section_header("Per-Class Accuracy Breakdown")
    pca = results["per_class_accuracy"]
    df = pd.DataFrame([
        {
            "Class": k,
            "Accuracy": f"{v:.1%}",
            "Crop": k.split(":")[0].strip(),
        }
        for k, v in sorted(pca.items(), key=lambda x: -x[1])
    ])
    st.dataframe(df, hide_index=True)
