"""Model architecture: MobileNetV2 with custom classification head."""
import torch.nn as nn
from torchvision import models

from src.config import UNFREEZE_LAST_N_BLOCKS


def build_model(num_classes, device, pretrained=True):
    """Build MobileNetV2 with frozen base and custom classifier.

    Returns (model, total_params, trainable_params).
    """
    weights = "IMAGENET1K_V1" if pretrained else None
    base_model = models.mobilenet_v2(weights=weights)

    # Freeze all base layers
    for param in base_model.parameters():
        param.requires_grad = False

    # Custom classification head
    base_model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(base_model.last_channel, 128),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(128, num_classes),
    )

    model = base_model.to(device)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    print(f"Total parameters:     {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    return model, total_params, trainable_params


def unfreeze_top_layers(model):
    """Unfreeze the last N feature blocks for fine-tuning."""
    for param in model.features[-UNFREEZE_LAST_N_BLOCKS:].parameters():
        param.requires_grad = True

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable parameters after unfreezing: {trainable:,}")
    return trainable
