"""Training logic: two-phase transfer learning with early stopping."""
import torch
import torch.nn as nn
import torch.optim as optim

from src.config import (
    NUM_EPOCHS_PHASE1, NUM_EPOCHS_PHASE2,
    LEARNING_RATE_PHASE1, LEARNING_RATE_PHASE2,
    PATIENCE, MODEL_PATH,
)
from src.models.classifier import unfreeze_top_layers


def train_one_epoch(model, loader, optimizer, criterion, device):
    """Train for one epoch. Returns (avg_loss, accuracy)."""
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
    return running_loss / total, correct / total


def evaluate(model, loader, criterion, device):
    """Evaluate on a data loader. Returns (avg_loss, accuracy)."""
    model.eval()
    running_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    return running_loss / total, correct / total


def _run_phase(model, train_loader, val_loader, optimizer, scheduler,
               criterion, device, num_epochs, history, best_val_acc, phase_name):
    """Generic training loop for one phase."""
    patience_counter = 0

    for epoch in range(num_epochs):
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)

        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        scheduler.step(val_acc)

        print(f"  Epoch {epoch + 1}/{num_epochs} — "
              f"Train: {train_acc:.4f}, Val: {val_acc:.4f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), MODEL_PATH)
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print(f"  Early stopping at epoch {epoch + 1}")
                break

    print(f"{phase_name} complete. Best Val Acc: {best_val_acc:.4f}")
    return best_val_acc


def train_model(model, train_loader, val_loader, class_weights_tensor, device):
    """Run the full two-phase training pipeline.

    Returns (history dict, best_val_acc, phase1_epochs).
    """
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    history = {"train_acc": [], "val_acc": [], "train_loss": [], "val_loss": []}
    best_val_acc = 0.0

    # Phase 1: Train classifier head only
    print("\nPhase 1: Training classifier head (base frozen)...")
    optimizer = optim.Adam(model.classifier.parameters(), lr=LEARNING_RATE_PHASE1)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)
    best_val_acc = _run_phase(model, train_loader, val_loader, optimizer, scheduler,
                              criterion, device, NUM_EPOCHS_PHASE1, history, best_val_acc, "Phase 1")
    phase1_epochs = len(history["train_acc"])

    # Phase 2: Fine-tune top layers
    print("\nPhase 2: Fine-tuning top layers...")
    unfreeze_top_layers(model)
    optimizer_ft = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=LEARNING_RATE_PHASE2)
    scheduler_ft = optim.lr_scheduler.ReduceLROnPlateau(optimizer_ft, mode="max", factor=0.5, patience=2)
    best_val_acc = _run_phase(model, train_loader, val_loader, optimizer_ft, scheduler_ft,
                              criterion, device, NUM_EPOCHS_PHASE2, history, best_val_acc, "Phase 2")

    return history, best_val_acc, phase1_epochs
