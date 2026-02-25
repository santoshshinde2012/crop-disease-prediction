"""Visualization: training history curves."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.config import PLOTS_DIR


def plot_training_history(history, phase1_epochs):
    """Save accuracy and loss curves."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    epochs_range = range(1, len(history["train_acc"]) + 1)

    ax1.plot(epochs_range, history["train_acc"], label="Train Accuracy", linewidth=2)
    ax1.plot(epochs_range, history["val_acc"], label="Validation Accuracy", linewidth=2)
    ax1.axvline(x=phase1_epochs, color="gray", linestyle="--", alpha=0.5, label="Fine-tuning starts")
    ax1.set_xlabel("Epoch"); ax1.set_ylabel("Accuracy")
    ax1.set_title("Model Accuracy", fontweight="bold"); ax1.legend(); ax1.grid(True, alpha=0.3)

    ax2.plot(epochs_range, history["train_loss"], label="Train Loss", linewidth=2)
    ax2.plot(epochs_range, history["val_loss"], label="Validation Loss", linewidth=2)
    ax2.axvline(x=phase1_epochs, color="gray", linestyle="--", alpha=0.5, label="Fine-tuning starts")
    ax2.set_xlabel("Epoch"); ax2.set_ylabel("Loss")
    ax2.set_title("Model Loss", fontweight="bold"); ax2.legend(); ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    path = PLOTS_DIR / "training_history.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
