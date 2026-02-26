#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# Crop Disease Classification — Universal Setup Script
#
# Sets up all prerequisites for notebooks, APIs, Streamlit,
# mobile app, and model export on macOS / Linux.
#
# Usage:
#   chmod +x scripts/setup.sh
#   ./scripts/setup.sh              # Interactive full setup
#   ./scripts/setup.sh --all        # Non-interactive full setup
#   ./scripts/setup.sh --python     # Python environment only
#   ./scripts/setup.sh --dataset    # Download dataset only
#   ./scripts/setup.sh --mobile     # Mobile app dependencies only
#   ./scripts/setup.sh --export     # TFLite export dependencies only
#   ./scripts/setup.sh --docker     # Docker setup only
#   ./scripts/setup.sh --verify     # Verify existing installation
# ──────────────────────────────────────────────────────────────

set -euo pipefail

# ── Constants ─────────────────────────────────────────────────
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_MIN_VERSION="3.10"
NODE_MIN_VERSION="18"
VENV_DIR="$PROJECT_ROOT/.venv"
REQUIRED_PYTHON_PACKAGES=(torch torchvision streamlit fastapi uvicorn jupyter tflite-runtime)

# ── Colors ────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ── Helpers ───────────────────────────────────────────────────

info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERR]${NC}  $*"; }
header()  { echo -e "\n${BOLD}${CYAN}═══ $* ═══${NC}\n"; }

command_exists() { command -v "$1" &>/dev/null; }

version_gte() {
    # Returns 0 if $1 >= $2 (semver-ish comparison)
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

detect_os() {
    case "$(uname -s)" in
        Darwin*) echo "macos" ;;
        Linux*)  echo "linux" ;;
        *)       echo "unknown" ;;
    esac
}

detect_arch() {
    case "$(uname -m)" in
        arm64|aarch64) echo "arm64" ;;
        x86_64)        echo "x86_64" ;;
        *)             echo "$(uname -m)" ;;
    esac
}

# ── Prerequisite Checks ──────────────────────────────────────

check_python() {
    header "Checking Python"

    if command_exists python3; then
        local py_version
        py_version=$(python3 --version 2>&1 | awk '{print $2}')
        if version_gte "$py_version" "$PYTHON_MIN_VERSION"; then
            success "Python $py_version (>= $PYTHON_MIN_VERSION)"
            return 0
        else
            warn "Python $py_version found, but >= $PYTHON_MIN_VERSION required"
        fi
    fi

    error "Python >= $PYTHON_MIN_VERSION not found"
    echo ""
    echo "  Install options:"
    if [ "$(detect_os)" = "macos" ]; then
        echo "    brew install python@3.11"
    else
        echo "    sudo apt install python3.11 python3.11-venv python3-pip   # Ubuntu/Debian"
        echo "    sudo dnf install python3.11                                # Fedora"
    fi
    echo "    Or use pyenv: https://github.com/pyenv/pyenv"
    return 1
}

check_node() {
    header "Checking Node.js"

    if command_exists node; then
        local node_version
        node_version=$(node --version | sed 's/^v//')
        if version_gte "$node_version" "$NODE_MIN_VERSION"; then
            success "Node.js $node_version (>= $NODE_MIN_VERSION)"
            return 0
        else
            warn "Node.js $node_version found, but >= $NODE_MIN_VERSION required"
        fi
    fi

    error "Node.js >= $NODE_MIN_VERSION not found"
    echo ""
    echo "  Install options:"
    if [ "$(detect_os)" = "macos" ]; then
        echo "    brew install node@20"
    else
        echo "    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
        echo "    sudo apt install nodejs"
    fi
    echo "    Or use nvm: https://github.com/nvm-sh/nvm"
    return 1
}

check_git() {
    if command_exists git; then
        success "Git $(git --version | awk '{print $3}')"
    else
        error "Git not found. Install: https://git-scm.com/downloads"
        return 1
    fi
}

check_optional_tools() {
    header "Checking Optional Tools"

    # Docker
    if command_exists docker; then
        success "Docker $(docker --version 2>/dev/null | awk '{print $3}' | tr -d ',')"
    else
        warn "Docker not found (optional — needed for containerized deployment)"
    fi

    # Kaggle CLI
    if command_exists kaggle; then
        success "Kaggle CLI installed"
    else
        warn "Kaggle CLI not found (optional — install with: pip install kaggle)"
    fi

    # ngrok
    if command_exists ngrok; then
        success "ngrok installed (for WhatsApp local dev)"
    else
        warn "ngrok not found (optional — needed for WhatsApp webhook testing)"
    fi

    # CocoaPods (macOS only)
    if [ "$(detect_os)" = "macos" ]; then
        if command_exists pod; then
            success "CocoaPods $(pod --version)"
        else
            warn "CocoaPods not found (required for iOS builds)"
            echo "       Install: sudo gem install cocoapods"
        fi

        # Xcode
        if command_exists xcodebuild; then
            success "Xcode $(xcodebuild -version 2>/dev/null | head -1 | awk '{print $2}')"
        else
            warn "Xcode not found (required for iOS builds)"
        fi
    fi

    # Java (Android)
    if command_exists java; then
        local java_version
        java_version=$(java -version 2>&1 | head -1 | awk -F'"' '{print $2}')
        success "Java $java_version (for Android builds)"
    else
        warn "Java not found (required for Android builds)"
    fi
}

# ── Setup Steps ───────────────────────────────────────────────

setup_python_env() {
    header "Setting Up Python Environment"

    # Create virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        info "Creating virtual environment at .venv/"
        python3 -m venv "$VENV_DIR"
        success "Virtual environment created"
    else
        success "Virtual environment already exists"
    fi

    # Activate
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    info "Activated virtual environment"

    # Upgrade pip
    info "Upgrading pip..."
    pip install --upgrade pip --quiet

    # Install core dependencies
    info "Installing Python dependencies from requirements.txt..."
    pip install -r "$PROJECT_ROOT/requirements.txt" --quiet
    success "Core Python packages installed"

    # Platform-specific torch info
    local os_name
    os_name=$(detect_os)
    local arch
    arch=$(detect_arch)

    if [ "$os_name" = "macos" ] && [ "$arch" = "arm64" ]; then
        info "Apple Silicon detected — PyTorch will use MPS acceleration"
    fi

    echo ""
    info "Activate the environment before running any Python commands:"
    echo "    source .venv/bin/activate"
}

setup_dataset() {
    header "Setting Up Dataset"

    local data_dir="$PROJECT_ROOT/data/raw/color"

    if [ -d "$data_dir" ] && [ "$(ls -A "$data_dir" 2>/dev/null)" ]; then
        success "Dataset already exists at data/raw/color/"
        return 0
    fi

    info "The PlantVillage dataset (~2 GB, ~54,000 images) is required."
    echo ""

    if command_exists kaggle; then
        info "Downloading via Kaggle CLI..."

        # Check kaggle credentials
        if [ ! -f "$HOME/.kaggle/kaggle.json" ]; then
            warn "Kaggle credentials not found."
            echo ""
            echo "  Setup Kaggle API:"
            echo "  1. Go to https://www.kaggle.com/settings → 'Create New Token'"
            echo "  2. Download kaggle.json"
            echo "  3. Run: mkdir -p ~/.kaggle && mv ~/Downloads/kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json"
            echo ""
            echo "  Then re-run: ./scripts/setup.sh --dataset"
            return 1
        fi

        cd "$PROJECT_ROOT"
        kaggle datasets download -d abdallahalidev/plantvillage-dataset -p "$PROJECT_ROOT"

        if [ -f "$PROJECT_ROOT/plantvillage-dataset.zip" ]; then
            info "Extracting dataset..."
            unzip -q "$PROJECT_ROOT/plantvillage-dataset.zip" -d "$PROJECT_ROOT/plantvillage-dataset"
            rm "$PROJECT_ROOT/plantvillage-dataset.zip"
            success "Dataset extracted"
        fi
    else
        info "Kaggle CLI not found. Manual download required:"
        echo ""
        echo "  Option A: Install Kaggle CLI"
        echo "    pip install kaggle"
        echo "    # Then re-run: ./scripts/setup.sh --dataset"
        echo ""
        echo "  Option B: Manual download"
        echo "    1. Go to https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset"
        echo "    2. Download and extract to: $PROJECT_ROOT/plantvillage-dataset/"
        echo ""
    fi

    # Create symlink
    local source_dir="$PROJECT_ROOT/plantvillage-dataset/plantvillage dataset/color"
    if [ -d "$source_dir" ]; then
        mkdir -p "$PROJECT_ROOT/data/raw"
        ln -sf "$source_dir" "$PROJECT_ROOT/data/raw/color"
        success "Data symlink created: data/raw/color -> plantvillage-dataset/..."
    else
        warn "Dataset directory not found. Create the symlink manually after download:"
        echo "    mkdir -p data/raw"
        echo "    ln -sf \"\$(pwd)/plantvillage-dataset/plantvillage dataset/color\" data/raw/color"
    fi
}

setup_env_file() {
    header "Setting Up Environment Variables"

    local env_file="$PROJECT_ROOT/.env"
    local env_example="$PROJECT_ROOT/.env.example"

    if [ -f "$env_file" ]; then
        success ".env file already exists"
    elif [ -f "$env_example" ]; then
        cp "$env_example" "$env_file"
        success "Created .env from .env.example"
        warn "Edit .env with your Twilio credentials (if using WhatsApp integration)"
    else
        warn ".env.example not found — skipping"
    fi
}

setup_export_deps() {
    header "Setting Up TFLite Export Dependencies"

    # Activate venv if not already
    if [ -z "${VIRTUAL_ENV:-}" ] && [ -d "$VENV_DIR" ]; then
        # shellcheck disable=SC1091
        source "$VENV_DIR/bin/activate"
    fi

    info "Installing ONNX and TensorFlow for model export..."
    pip install onnx==1.16.2 onnx2tf tensorflow --quiet
    success "Export dependencies installed (onnx, onnx2tf, tensorflow)"

    echo ""
    info "To export the model:"
    echo "    python scripts/export_model.py"
}

setup_mobile() {
    header "Setting Up Mobile App (React Native)"

    local mobile_dir="$PROJECT_ROOT/mobile"

    if [ ! -d "$mobile_dir" ]; then
        error "Mobile directory not found at $mobile_dir"
        return 1
    fi

    cd "$mobile_dir"

    # npm install
    info "Installing npm dependencies..."
    npm install --silent 2>/dev/null || npm install
    success "npm packages installed"

    # iOS pods (macOS only)
    if [ "$(detect_os)" = "macos" ]; then
        if command_exists pod; then
            if [ -d "$mobile_dir/ios" ]; then
                info "Installing CocoaPods dependencies..."
                cd "$mobile_dir/ios"
                pod install --silent 2>/dev/null || pod install
                cd "$mobile_dir"
                success "iOS pods installed"
            fi
        else
            warn "CocoaPods not found — skipping iOS pod install"
            echo "       Install: sudo gem install cocoapods"
        fi
    fi

    # Check TFLite model exists
    local model_path="$mobile_dir/assets/model/crop_disease_classifier.tflite"
    if [ -f "$model_path" ]; then
        success "TFLite model found at mobile/assets/model/"
    else
        warn "TFLite model not found at mobile/assets/model/"
        echo "       Run the notebook first (Step 2), then export:"
        echo "       python scripts/export_model.py"
    fi

    cd "$PROJECT_ROOT"
}

setup_docker() {
    header "Setting Up Docker"

    if ! command_exists docker; then
        error "Docker not found. Install from: https://docs.docker.com/get-docker/"
        return 1
    fi

    if ! docker info &>/dev/null; then
        error "Docker daemon is not running. Start Docker Desktop or the Docker service."
        return 1
    fi

    info "Building Docker image..."
    cd "$PROJECT_ROOT"
    docker compose build
    success "Docker image built"

    echo ""
    info "Run the API container:"
    echo "    docker compose up"
}

# ── Verification ──────────────────────────────────────────────

verify_installation() {
    header "Verifying Installation"

    local all_ok=true

    # Python environment
    if [ -d "$VENV_DIR" ]; then
        success "Python virtual environment (.venv/)"
    else
        warn "Python virtual environment not found"
        all_ok=false
    fi

    # Key Python packages
    if [ -d "$VENV_DIR" ]; then
        # shellcheck disable=SC1091
        source "$VENV_DIR/bin/activate"
        for pkg in "${REQUIRED_PYTHON_PACKAGES[@]}"; do
            # tflite-runtime installs as tflite_runtime
            local import_name="${pkg//-/_}"
            if python3 -c "import $import_name" 2>/dev/null; then
                success "Python: $pkg"
            else
                warn "Python: $pkg not importable"
                all_ok=false
            fi
        done
    fi

    # Dataset
    if [ -d "$PROJECT_ROOT/data/raw/color" ] && [ "$(ls -A "$PROJECT_ROOT/data/raw/color" 2>/dev/null)" ]; then
        local class_count
        class_count=$(ls -d "$PROJECT_ROOT/data/raw/color"/*/ 2>/dev/null | wc -l | tr -d ' ')
        success "Dataset: $class_count classes in data/raw/color/"
    else
        warn "Dataset not found at data/raw/color/"
        all_ok=false
    fi

    # Trained model
    if [ -f "$PROJECT_ROOT/checkpoints/best_model.pth" ]; then
        local model_size
        model_size=$(du -h "$PROJECT_ROOT/checkpoints/best_model.pth" | awk '{print $1}')
        success "Trained model: checkpoints/best_model.pth ($model_size)"
    else
        warn "Trained model not found (run notebook first)"
        all_ok=false
    fi

    # TFLite export
    if [ -f "$PROJECT_ROOT/exports/crop_disease_classifier.tflite" ]; then
        success "TFLite export: exports/crop_disease_classifier.tflite"
    else
        warn "TFLite export not found (run: python scripts/export_model.py)"
        all_ok=false
    fi

    # Metrics
    if [ -f "$PROJECT_ROOT/outputs/metrics/class_names.json" ]; then
        success "Metrics: outputs/metrics/class_names.json"
    else
        warn "Metrics not found (generated by notebook)"
        all_ok=false
    fi

    # .env
    if [ -f "$PROJECT_ROOT/.env" ]; then
        success "Environment: .env file"
    else
        warn ".env file not found (needed for WhatsApp)"
        all_ok=false
    fi

    # Mobile dependencies
    if [ -d "$PROJECT_ROOT/mobile/node_modules" ]; then
        success "Mobile: node_modules/"
    else
        warn "Mobile: node_modules not found (run: cd mobile && npm install)"
        all_ok=false
    fi

    # Mobile TFLite model
    if [ -f "$PROJECT_ROOT/mobile/assets/model/crop_disease_classifier.tflite" ]; then
        success "Mobile: TFLite model bundled"
    else
        warn "Mobile: TFLite model not bundled"
        all_ok=false
    fi

    # iOS pods
    if [ "$(detect_os)" = "macos" ] && [ -d "$PROJECT_ROOT/mobile/ios" ]; then
        if [ -d "$PROJECT_ROOT/mobile/ios/Pods" ]; then
            success "Mobile: iOS Pods installed"
        else
            warn "Mobile: iOS Pods not installed (run: cd mobile/ios && pod install)"
            all_ok=false
        fi
    fi

    echo ""
    if [ "$all_ok" = true ]; then
        success "All checks passed! Project is ready."
    else
        warn "Some items need attention (see warnings above)."
    fi
}

# ── Full Setup ────────────────────────────────────────────────

full_setup() {
    header "Crop Disease Classification — Full Setup"

    info "Platform: $(detect_os) / $(detect_arch)"
    info "Project:  $PROJECT_ROOT"
    echo ""

    # Prerequisites
    check_python || return 1
    check_node || return 1
    check_git || return 1
    check_optional_tools

    # Core setup
    setup_python_env
    setup_env_file
    setup_dataset
    setup_export_deps
    setup_mobile

    # Verification
    verify_installation

    echo ""
    header "Setup Complete — Quick Start"
    echo "  ${BOLD}Activate environment:${NC}"
    echo "    source .venv/bin/activate"
    echo ""
    echo "  ${BOLD}1. Jupyter Notebook${NC} (train model):"
    echo "    jupyter notebook notebooks/crop_disease_classification.ipynb"
    echo ""
    echo "  ${BOLD}2. Streamlit App${NC} (web UI):"
    echo "    streamlit run streamlit_app/app.py"
    echo ""
    echo "  ${BOLD}3. REST API${NC} (backend):"
    echo "    uvicorn api.main:app --reload"
    echo ""
    echo "  ${BOLD}4. Export TFLite${NC} (for mobile):"
    echo "    python scripts/export_model.py"
    echo ""
    echo "  ${BOLD}5. Mobile App${NC} (React Native):"
    echo "    cd mobile && npm run ios    # or: npm run android"
    echo ""
    echo "  ${BOLD}6. Docker${NC} (containerized API):"
    echo "    docker compose up --build"
    echo ""
    echo "  See wiki/setup-guide.md for detailed documentation."
}

# ── Interactive Menu ──────────────────────────────────────────

interactive_menu() {
    header "Crop Disease Classification — Setup"

    echo "  Platform: $(detect_os) / $(detect_arch)"
    echo "  Project:  $PROJECT_ROOT"
    echo ""
    echo "  What would you like to set up?"
    echo ""
    echo "    1) Full setup (everything)"
    echo "    2) Python environment only"
    echo "    3) Download dataset only"
    echo "    4) TFLite export dependencies"
    echo "    5) Mobile app dependencies"
    echo "    6) Docker build"
    echo "    7) Verify installation"
    echo "    8) Exit"
    echo ""

    read -rp "  Choose [1-8]: " choice

    case "$choice" in
        1) full_setup ;;
        2) check_python && setup_python_env ;;
        3) setup_dataset ;;
        4) setup_export_deps ;;
        5) check_node && setup_mobile ;;
        6) setup_docker ;;
        7) verify_installation ;;
        8) echo "Bye!"; exit 0 ;;
        *) error "Invalid choice"; exit 1 ;;
    esac
}

# ── CLI Entry Point ───────────────────────────────────────────

cd "$PROJECT_ROOT"

case "${1:-}" in
    --all)     full_setup ;;
    --python)  check_python && setup_python_env ;;
    --dataset) setup_dataset ;;
    --export)  setup_export_deps ;;
    --mobile)  check_node && setup_mobile ;;
    --docker)  setup_docker ;;
    --verify)  verify_installation ;;
    --help|-h)
        echo "Usage: ./scripts/setup.sh [OPTION]"
        echo ""
        echo "Options:"
        echo "  --all       Non-interactive full setup"
        echo "  --python    Python environment only"
        echo "  --dataset   Download dataset only"
        echo "  --export    TFLite export dependencies"
        echo "  --mobile    Mobile app dependencies"
        echo "  --docker    Docker build"
        echo "  --verify    Verify existing installation"
        echo "  --help      Show this help"
        echo ""
        echo "No arguments launches the interactive menu."
        ;;
    "")        interactive_menu ;;
    *)         error "Unknown option: $1. Use --help for usage."; exit 1 ;;
esac
