import { loadTensorflowModel, TensorflowModel } from 'react-native-fast-tflite';
import { Platform } from 'react-native';
import classNames from '../../assets/data/class_names.json';
import diseaseInfo from '../../assets/data/disease_info.json';
import type { PredictionResult, ClassPrediction, Disease, DiseaseDatabase } from '../types';

// ImageNet normalization constants (matches src/config.py)
const IMAGENET_MEAN = [0.485, 0.456, 0.406];
const IMAGENET_STD = [0.229, 0.224, 0.225];
const IMG_SIZE = 224;
const NUM_CLASSES = 15;
const TOP_K = 5;

/** Minimum confidence to consider a prediction reliable */
export const CONFIDENCE_THRESHOLD = 0.5;

const diseases = diseaseInfo as DiseaseDatabase;

let model: TensorflowModel | null = null;
let inputLayout: 'nhwc' | 'nchw' = 'nhwc';

/**
 * Load TFLite model for on-device inference.
 *
 * Uses platform-specific hardware acceleration:
 * - iOS: CoreML delegate (Neural Engine / GPU)
 * - Android: GPU delegate, fallback to CPU
 */
export async function loadModel(): Promise<void> {
  if (model) return;

  const delegate = Platform.OS === 'ios' ? 'core-ml' : 'android-gpu';

  try {
    model = await loadTensorflowModel(
      require('../../assets/model/crop_disease_classifier.tflite'),
      delegate,
    );
  } catch {
    // Fallback to CPU if hardware delegate unavailable
    model = await loadTensorflowModel(
      require('../../assets/model/crop_disease_classifier.tflite'),
    );
  }

  // Detect input layout from model metadata
  const shape = model.inputs[0].shape;
  inputLayout = shape[1] === 3 ? 'nchw' : 'nhwc';
}

/** Check if model is loaded and ready */
export function isModelLoaded(): boolean {
  return model !== null;
}

/** Softmax over raw logits — numerically stable */
function softmax(logits: number[]): number[] {
  const maxVal = Math.max(...logits);
  const exps = logits.map((v) => Math.exp(v - maxVal));
  const sumExps = exps.reduce((a, b) => a + b, 0);
  return exps.map((v) => v / sumExps);
}

/**
 * Preprocess raw RGBA pixel data into a normalized float32 tensor.
 *
 * Pipeline (matches src/inference/predictor.py):
 *   1. Read RGB channels from RGBA buffer (skip alpha)
 *   2. Scale to [0, 1]
 *   3. Normalize with ImageNet mean/std
 *   4. Layout as NHWC or NCHW depending on model input shape
 *
 * @param rgbaData - Raw pixel buffer (RGBA format, must be 224x224)
 * @returns Float32Array matching model input shape
 */
export function preprocessPixels(rgbaData: Uint8Array): Float32Array {
  const expectedLength = IMG_SIZE * IMG_SIZE * 4;
  if (rgbaData.length !== expectedLength) {
    throw new Error(
      `Invalid pixel data: expected ${expectedLength} bytes (224x224 RGBA), got ${rgbaData.length}`,
    );
  }

  const pixelCount = IMG_SIZE * IMG_SIZE;
  const tensor = new Float32Array(pixelCount * 3);

  if (inputLayout === 'nchw') {
    // NCHW: [1, 3, 224, 224] — channels first (PyTorch convention)
    for (let i = 0; i < pixelCount; i++) {
      const rgbaOffset = i * 4;
      for (let c = 0; c < 3; c++) {
        const value = rgbaData[rgbaOffset + c] / 255.0;
        tensor[c * pixelCount + i] = (value - IMAGENET_MEAN[c]) / IMAGENET_STD[c];
      }
    }
  } else {
    // NHWC: [1, 224, 224, 3] — channels last (TFLite convention)
    for (let i = 0; i < pixelCount; i++) {
      const rgbaOffset = i * 4;
      const tensorOffset = i * 3;
      for (let c = 0; c < 3; c++) {
        const value = rgbaData[rgbaOffset + c] / 255.0;
        tensor[tensorOffset + c] = (value - IMAGENET_MEAN[c]) / IMAGENET_STD[c];
      }
    }
  }

  return tensor;
}

/**
 * Run disease classification on preprocessed image data.
 *
 * @param inputTensor - Preprocessed Float32Array [1, 3, 224, 224] or [1, 224, 224, 3]
 * @returns Full prediction result with disease info, top-K predictions
 * @throws Error if model not loaded or output is malformed
 */
export async function predict(inputTensor: Float32Array): Promise<PredictionResult> {
  if (!model) {
    throw new Error('Model not loaded. Call loadModel() first.');
  }

  const output = await model.run([inputTensor]);
  const rawOutput = output[0];

  if (!rawOutput || rawOutput.length !== NUM_CLASSES) {
    throw new Error(
      `Unexpected model output: expected ${NUM_CLASSES} values, got ${rawOutput?.length ?? 0}`,
    );
  }

  const logits = Array.from(rawOutput as Float32Array);

  // Apply softmax to get probabilities
  const probabilities = softmax(logits);

  // Sort by confidence descending
  const indexed = probabilities.map((prob, idx) => ({ idx, prob }));
  indexed.sort((a, b) => b.prob - a.prob);

  // Top prediction
  const topIdx = indexed[0].idx;
  const diseaseName = classNames[topIdx];
  const confidence = indexed[0].prob;
  const details: Disease | undefined = diseases[diseaseName];

  // Top-K predictions
  const topK: ClassPrediction[] = indexed.slice(0, TOP_K).map((item) => ({
    className: classNames[item.idx],
    confidence: item.prob,
  }));

  return {
    disease: diseaseName,
    confidence,
    crop: details?.crop ?? diseaseName.split(':')[0].trim(),
    severity: details?.severity ?? 'None',
    treatment: details?.treatment ?? 'Consult a local agronomist for specific treatment.',
    symptoms: details?.symptoms ?? [],
    prevention: details?.prevention ?? [],
    topK,
  };
}

/** Release model resources */
export function releaseModel(): void {
  model = null;
}
