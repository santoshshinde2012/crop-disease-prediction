import { useState, useCallback } from 'react';
import { useModel } from '../context/ModelContext';
import { extractPixels } from '../services/imageProcessor';
import { savePrediction } from '../services/storage';
import type { PredictionResult } from '../types';

interface UsePredictionReturn {
  /** Whether a prediction is currently running */
  loading: boolean;
  /** The most recent prediction result */
  result: PredictionResult | null;
  /** Error message if prediction failed */
  error: string | null;
  /** Analyze a leaf image: extract pixels → predict → save to history */
  analyze: (imagePath: string) => Promise<PredictionResult | null>;
  /** Clear the current result */
  reset: () => void;
}

/**
 * Orchestrates the full prediction pipeline.
 *
 * Separation of concerns:
 *   - imageProcessor handles image I/O (resize + pixel extraction)
 *   - ModelContext handles ML inference (preprocess + predict)
 *   - storage handles persistence (save to AsyncStorage)
 *   - This hook manages UI state (loading, error, result)
 */
export function usePrediction(): UsePredictionReturn {
  const { runPrediction, isReady } = useModel();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(
    async (imagePath: string): Promise<PredictionResult | null> => {
      if (!isReady) {
        setError('Model is still loading. Please wait.');
        return null;
      }

      setLoading(true);
      setError(null);

      try {
        const rgbaPixels = await extractPixels(imagePath);
        const prediction = await runPrediction(rgbaPixels);
        setResult(prediction);

        await savePrediction(prediction, imagePath);

        return prediction;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Prediction failed.';
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [runPrediction, isReady],
  );

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { loading, result, error, analyze, reset };
}
