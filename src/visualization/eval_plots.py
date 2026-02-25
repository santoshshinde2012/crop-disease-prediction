"""Visualization: evaluation plots (confusion matrix, predictions, per-class accuracy)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

from src.config import PLOTS_DIR


def plot_confusion_matrix(y_true, y_pred, class_names):
    """Heatmap of the confusion matrix."""
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(16, 14))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names,
                ax=ax, linewidths=0.5)
    ax.set_xlabel("Predicted Label", fontsize=12)
    ax.set_ylabel("True Label", fontsize=12)
    ax.set_title("Confusion Matrix — Crop Disease Classification", fontsize=14, fontweight="bold")
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    path = PLOTS_DIR / "confusion_matrix.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
    return cm


def plot_correct_incorrect(y_true, y_pred, y_probs, images_viz, class_names):
    """Show 5 correct and 5 incorrect predictions."""
    correct_mask = y_true == y_pred

    # 5 correct (highest confidence)
    correct_idx = np.where(correct_mask)[0]
    selected = correct_idx[np.argsort(-y_probs[correct_idx])[:5]]

    fig, axes = plt.subplots(1, 5, figsize=(20, 4))
    fig.suptitle("5 Correct Predictions", fontsize=14, fontweight="bold", color="green")
    for i, idx in enumerate(selected):
        axes[i].imshow(images_viz[idx])
        axes[i].set_title(
            f"True: {class_names[y_true[idx]]}\nPred: {class_names[y_pred[idx]]}\nConf: {y_probs[idx]:.2%}",
            fontsize=8, color="green")
        axes[i].axis("off")
    plt.tight_layout()
    path = PLOTS_DIR / "correct_predictions.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")

    # 5 incorrect (highest confidence errors)
    incorrect_idx = np.where(~correct_mask)[0]
    if len(incorrect_idx) == 0:
        print("No incorrect predictions!")
        return

    n = min(5, len(incorrect_idx))
    selected = incorrect_idx[np.argsort(-y_probs[incorrect_idx])[:n]]

    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axes = [axes]
    fig.suptitle("Incorrect Predictions (Highest Confidence Errors)", fontsize=14, fontweight="bold", color="red")
    for i, idx in enumerate(selected):
        axes[i].imshow(images_viz[idx])
        axes[i].set_title(
            f"True: {class_names[y_true[idx]]}\nPred: {class_names[y_pred[idx]]}\nConf: {y_probs[idx]:.2%}",
            fontsize=8, color="red")
        axes[i].axis("off")
    plt.tight_layout()
    path = PLOTS_DIR / "incorrect_predictions.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def plot_per_class_accuracy(cm, class_names):
    """Bar chart of per-class accuracy with color coding."""
    num_classes = len(class_names)
    per_class_acc = cm.diagonal() / cm.sum(axis=1)

    fig, ax = plt.subplots(figsize=(14, 6))
    colors = ["#27ae60" if a >= 0.9 else "#f39c12" if a >= 0.8 else "#e74c3c" for a in per_class_acc]
    bars = ax.bar(range(num_classes), per_class_acc, color=colors, edgecolor="white")
    ax.set_xticks(range(num_classes))
    ax.set_xticklabels(class_names, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Accuracy", fontsize=12)
    ax.set_title("Per-Class Accuracy", fontsize=14, fontweight="bold")
    ax.axhline(y=0.9, color="green", linestyle="--", alpha=0.5, label="90% threshold")
    ax.set_ylim(0, 1.05)
    for bar, a in zip(bars, per_class_acc):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{a:.1%}", ha="center", fontsize=8)
    ax.legend(fontsize=10)
    plt.tight_layout()
    path = PLOTS_DIR / "per_class_accuracy.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
    return per_class_acc
