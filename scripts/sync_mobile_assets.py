"""
Sync shared data from src/ to mobile/assets/data/.

Ensures the mobile app's bundled JSON files stay in sync with the
Python source of truth. Run after notebook training to update.

Usage:
    cd crop-prediction
    python scripts/sync_mobile_assets.py
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.disease_info import DISEASE_INFO
from src.config import CLASS_NAMES_PATH

MOBILE_DATA_DIR = PROJECT_ROOT / "mobile" / "assets" / "data"


def sync():
    MOBILE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Sync class names
    class_names = json.loads(CLASS_NAMES_PATH.read_text())
    (MOBILE_DATA_DIR / "class_names.json").write_text(
        json.dumps(class_names, indent=2) + "\n"
    )

    # Sync disease info
    (MOBILE_DATA_DIR / "disease_info.json").write_text(
        json.dumps(DISEASE_INFO, indent=2) + "\n"
    )

    print(f"Synced to {MOBILE_DATA_DIR}")
    print(f"  class_names.json: {len(class_names)} classes")
    print(f"  disease_info.json: {len(DISEASE_INFO)} diseases")


if __name__ == "__main__":
    sync()
