"""Visualization: dataset exploration plots."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from torchvision import datasets

from src.config import DATA_DIR, FILTERED_DIR, SELECTED_CLASSES, DISPLAY_NAMES, PLOTS_DIR
from src.data.transforms import aug_visual_transform


def plot_class_distribution(class_counts):
    """Bar chart coloured by crop type."""
    fig, ax = plt.subplots(figsize=(14, 7))
    names = list(class_counts.keys())
    counts = list(class_counts.values())

    colors = []
    for name in names:
        if name.startswith("Tomato"):
            colors.append("#e74c3c")
        elif name.startswith("Potato"):
            colors.append("#f39c12")
        else:
            colors.append("#27ae60")

    bars = ax.bar(range(len(names)), counts, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Number of Images", fontsize=12)
    ax.set_title("Class Distribution Across Selected 15 Disease Classes", fontsize=14, fontweight="bold")
    ax.axhline(y=np.mean(counts), color="gray", linestyle="--", alpha=0.7)

    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30, str(count),
                ha="center", va="bottom", fontsize=8)

    legend_elements = [
        Patch(facecolor="#e74c3c", label="Tomato"),
        Patch(facecolor="#f39c12", label="Potato"),
        Patch(facecolor="#27ae60", label="Corn"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=10)
    plt.tight_layout()
    path = PLOTS_DIR / "class_distribution.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def plot_sample_images():
    """Grid of 5 classes x 4 sample images."""
    sample_classes = [
        "Tomato___Bacterial_spot",
        "Tomato___Late_blight",
        "Potato___Early_blight",
        "Corn_(maize)___Common_rust_",
        "Tomato___healthy",
    ]
    fig, axes = plt.subplots(5, 4, figsize=(16, 20))
    fig.suptitle("Sample Images from 5 Disease Classes", fontsize=16, fontweight="bold", y=1.01)

    for row, cls in enumerate(sample_classes):
        class_dir = DATA_DIR / cls
        images_list = sorted(class_dir.glob("*"))[:4]
        for col, img_path in enumerate(images_list):
            img = plt.imread(str(img_path))
            axes[row, col].imshow(img)
            axes[row, col].axis("off")
            if col == 0:
                axes[row, col].set_title(DISPLAY_NAMES[cls], fontsize=11, fontweight="bold", loc="left")

    plt.tight_layout()
    path = PLOTS_DIR / "sample_images.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def plot_augmentation_examples():
    """Visualise augmentation on a single sample image."""
    full_dataset_raw = datasets.ImageFolder(str(FILTERED_DIR))
    raw_img, _ = full_dataset_raw[0]

    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    fig.suptitle("Data Augmentation Examples", fontsize=14, fontweight="bold")

    axes[0, 0].imshow(raw_img)
    axes[0, 0].set_title("Original", fontweight="bold")
    axes[0, 0].axis("off")

    for i in range(1, 10):
        row, col = divmod(i, 5)
        aug_img = aug_visual_transform(raw_img)
        axes[row, col].imshow(aug_img)
        axes[row, col].set_title(f"Augmented #{i}")
        axes[row, col].axis("off")

    plt.tight_layout()
    path = PLOTS_DIR / "augmentation_examples.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def print_insights(class_counts):
    """Print 3 key dataset insights."""
    max_count = max(class_counts.values())
    min_count = min(class_counts.values())
    max_class = [k for k, v in class_counts.items() if v == max_count][0]
    min_class = [k for k, v in class_counts.items() if v == min_count][0]

    print(f"\nINSIGHT 1: Class Imbalance — "
          f"{max_class} ({max_count}) vs {min_class} ({min_count}), ratio {max_count / min_count:.1f}x")

    crop_totals = {}
    for name, count in class_counts.items():
        crop = name.split(":")[0]
        crop_totals[crop] = crop_totals.get(crop, 0) + count
    print("INSIGHT 2: Crop distribution — "
          + ", ".join(f"{c}: {t:,}" for c, t in sorted(crop_totals.items(), key=lambda x: -x[1])))

    sample_dir = DATA_DIR / SELECTED_CLASSES[0]
    sample_img_path = next(sample_dir.glob("*"))
    sample_img = plt.imread(str(sample_img_path))
    print(f"INSIGHT 3: Images are {sample_img.shape[0]}x{sample_img.shape[1]} RGB, dtype={sample_img.dtype}")
