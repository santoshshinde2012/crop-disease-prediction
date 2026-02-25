import { InferenceSession, Tensor } from 'onnxruntime-react-native';
import RNFS from 'react-native-fs';
import { Platform } from 'react-native';
import classNames from '../../assets/data/class_names.json';
import diseaseInfo from '../../assets/data/disease_info.json';
import type { PredictionResult, ClassPrediction, Disease, DiseaseDatabase } from '../types';

// ImageNet normalization constants (from src/config.py)
const IMAGENET_MEAN = [0.485, 0.456, 0.406];
const IMAGENET_STD = [0.229, 0.224, 0.225];
const IMG_SIZE = 224;
const NUM_CLASSES = 15;
const TOP_K = 5;
const CONFIDENCE_THRESHOLD = 0.5;

const diseases = diseaseInfo as DiseaseDatabase;

let session: InferenceSession | null = null;

/**
 * Get the path to the bundled ONNX model asset.
 *
 * On iOS, assets are in the main bundle.
 * On Android, they need to be copied from the APK to a readable location.
 */
async function getModelPath(): Promise<string> {
  const modelName = 'crop_disease_classifier.onnx';

  if (Platform.OS === 'ios') {
    // On iOS, bundled assets are in the main bundle
    const bundlePath = `${RNFS.MainBundlePath}/${modelName}`;
    const exists = await RNFS.exists(bundlePath);
    if (exists) return bundlePath;

    // Fallback: check assets directory
    const assetsPath = `${RNFS.MainBundlePath}/assets/model/${modelName}`;
    return assetsPath;
  }

  // On Android, copy from assets to document directory
  const destPath = `${RNFS.DocumentDirectoryPath}/${modelName}`;
  const exists = await RNFS.exists(destPath);
  if (!exists) {
    await RNFS.copyFileAssets(`model/${modelName}`, destPath);
  }
  return destPath;
}

/**
 * Load ONNX model for inference.
 *
 * Uses ONNX Runtime which provides:
 * - iOS: CoreML execution provider (Neural Engine / GPU)
 * - Android: NNAPI execution provider, fallback to CPU
 */
export async function loadModel(): Promise<InferenceSession> {
  if (session) return session;

  const modelPath = await getModelPath();
  session = await InferenceSession.create(modelPath);

  return session;
}

/** Check if model is loaded and ready */
export function isModelLoaded(): boolean {
  return session !== null;
}

/** Softmax over raw logits — numerically stable */
function softmax(logits: number[]): number[] {
  const maxVal = Math.max(...logits);
  const exps = logits.map((v) => Math.exp(v - maxVal));
  const sumExps = exps.reduce((a, b) => a + b, 0);
  return exps.map((v) => v / sumExps);
}

/**
 * Preprocess raw RGBA pixel data into normalized CHW float32 tensor.
 *
 * Pipeline (matches src/inference/predictor.py):
 *   1. Read RGB channels from RGBA buffer (skip alpha)
 *   2. Scale to [0, 1]
 *   3. Normalize with ImageNet mean/std
 *   4. Layout as CHW (channels-first) for the model
 *
 * @param rgbaData - Raw pixel buffer (RGBA format, must be 224x224)
 * @returns Float32Array shaped [1, 3, 224, 224]
 */
export function preprocessPixels(rgbaData: Uint8Array): Float32Array {
  const expectedLength = IMG_SIZE * IMG_SIZE * 4;
  if (rgbaData.length !== expectedLength) {
    throw new Error(
      `Invalid pixel data: expected ${expectedLength} bytes (224x224 RGBA), got ${rgbaData.length}`,
    );
  }

  const tensor = new Float32Array(1 * 3 * IMG_SIZE * IMG_SIZE);
  const pixelCount = IMG_SIZE * IMG_SIZE;

  for (let i = 0; i < pixelCount; i++) {
    const rgbaOffset = i * 4;
    for (let c = 0; c < 3; c++) {
      const value = rgbaData[rgbaOffset + c] / 255.0;
      const normalized = (value - IMAGENET_MEAN[c]) / IMAGENET_STD[c];
      tensor[c * pixelCount + i] = normalized;
    }
  }

  return tensor;
}

/**
 * Run disease classification on preprocessed image data.
 *
 * @param inputTensor - Preprocessed Float32Array [1, 3, 224, 224]
 * @returns Full prediction result with disease info, top-K predictions
 * @throws Error if model not loaded or output is malformed
 */
export async function predict(inputTensor: Float32Array): Promise<PredictionResult> {
  if (!session) {
    throw new Error('Model not loaded. Call loadModel() first.');
  }

  // Create ONNX Runtime tensor
  const feeds = {
    input: new Tensor('float32', inputTensor, [1, 3, IMG_SIZE, IMG_SIZE]),
  };

  // Run inference
  const output = await session.run(feeds);
  const outputTensor = output.output;

  if (!outputTensor || outputTensor.data.length !== NUM_CLASSES) {
    throw new Error(
      `Unexpected model output: expected ${NUM_CLASSES} values, got ${outputTensor?.data.length ?? 0}`,
    );
  }

  const logits = Array.from(outputTensor.data as Float32Array);

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

/** Minimum confidence to consider a prediction reliable */
export { CONFIDENCE_THRESHOLD };

/** Release model resources */
export function releaseModel(): void {
  session = null;
}
