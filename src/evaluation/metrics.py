"""Model evaluation: prediction collection and classification metrics."""
import numpy as np
import torch
from sklearn.metrics import classification_report

from src.data.transforms import inv_normalize


def collect_predictions(model, val_loader, device):
    """Run the model on the validation set and collect predictions."""
    model.eval()
    y_true, y_pred, y_probs, images_viz = [], [], [], []

    with torch.no_grad():
        for images, labels in val_loader:
            outputs = model(images.to(device))
            probs = torch.softmax(outputs, dim=1)
            max_probs, predicted = probs.max(1)

            y_true.extend(labels.numpy())
            y_pred.extend(predicted.cpu().numpy())
            y_probs.extend(max_probs.cpu().numpy())

            for img in images:
                img_viz = inv_normalize(img).permute(1, 2, 0).numpy()
                img_viz = np.clip(img_viz, 0, 1)
                images_viz.append(img_viz)

    return (np.array(y_true), np.array(y_pred),
            np.array(y_probs), images_viz)


def print_classification_report(y_true, y_pred, class_names):
    """Print accuracy and full classification report."""
    accuracy = np.mean(y_true == y_pred)
    print(f"Validation Accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=class_names, digits=3))
    return accuracy
