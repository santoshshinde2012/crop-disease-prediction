"""
Central configuration for the Crop Disease Classification pipeline.
All paths, hyperparameters, and constants in one place.
"""
from pathlib import Path

# ── Project paths ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "raw" / "color"
FILTERED_DIR = PROJECT_ROOT / "data" / "processed"
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"
PLOTS_DIR = PROJECT_ROOT / "outputs" / "plots"
METRICS_DIR = PROJECT_ROOT / "outputs" / "metrics"

MODEL_PATH = CHECKPOINTS_DIR / "best_model.pth"
CLASS_NAMES_PATH = METRICS_DIR / "class_names.json"
RESULTS_PATH = METRICS_DIR / "results.json"
SUMMARY_CSV_PATH = METRICS_DIR / "model_performance_summary.csv"

# ── Hyperparameters ────────────────────────────────────────────
IMG_SIZE = 224
BATCH_SIZE = 32
SEED = 42
NUM_EPOCHS_PHASE1 = 5
NUM_EPOCHS_PHASE2 = 10
LEARNING_RATE_PHASE1 = 1e-3
LEARNING_RATE_PHASE2 = 1e-4
PATIENCE = 3
UNFREEZE_LAST_N_BLOCKS = 5

# ── ImageNet normalisation ─────────────────────────────────────
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# ── Class definitions ──────────────────────────────────────────
SELECTED_CLASSES = [
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
]

DISPLAY_NAMES = {
    "Tomato___Bacterial_spot": "Tomato: Bacterial Spot",
    "Tomato___Early_blight": "Tomato: Early Blight",
    "Tomato___Late_blight": "Tomato: Late Blight",
    "Tomato___Leaf_Mold": "Tomato: Leaf Mold",
    "Tomato___Septoria_leaf_spot": "Tomato: Septoria Leaf Spot",
    "Tomato___Target_Spot": "Tomato: Target Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Tomato: Yellow Leaf Curl",
    "Tomato___healthy": "Tomato: Healthy",
    "Potato___Early_blight": "Potato: Early Blight",
    "Potato___Late_blight": "Potato: Late Blight",
    "Potato___healthy": "Potato: Healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Corn: Gray Leaf Spot",
    "Corn_(maize)___Common_rust_": "Corn: Common Rust",
    "Corn_(maize)___Northern_Leaf_Blight": "Corn: Northern Leaf Blight",
    "Corn_(maize)___healthy": "Corn: Healthy",
}


def ensure_dirs():
    """Create output directories. Call explicitly from pipeline entry points."""
    for d in [CHECKPOINTS_DIR, PLOTS_DIR, METRICS_DIR, FILTERED_DIR]:
        d.mkdir(parents=True, exist_ok=True)
