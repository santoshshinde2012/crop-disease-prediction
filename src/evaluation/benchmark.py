"""Inference speed benchmarking."""
import time

import numpy as np
import torch

from src.config import IMG_SIZE


def benchmark_inference(model, device):
    """Measure average inference time over 50 runs."""
    sample = torch.randn(1, 3, IMG_SIZE, IMG_SIZE).to(device)
    with torch.no_grad():
        _ = model(sample)  # warmup

    times = []
    with torch.no_grad():
        for _ in range(50):
            start = time.time()
            _ = model(sample)
            if device.type == "mps":
                torch.mps.synchronize()
            elif device.type == "cuda":
                torch.cuda.synchronize()
            times.append(time.time() - start)

    return np.mean(times) * 1000
