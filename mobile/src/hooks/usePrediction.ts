import { useState, useCallback } from 'react';
import { useModel } from '../context/ModelContext';
import { savePrediction } from '../services/storage';
import type { PredictionResult } from '../types';

interface UsePredictionReturn {
  /** Whether a prediction is currently running */
  loading: boolean;
  /** The most recent prediction result */
  result: PredictionResult | null;
  /** Error message if prediction failed */
  error: string | null;
  /** Run prediction on RGBA pixel data and save to history */
  analyze: (rgbaData: Uint8Array, imagePath: string) => Promise<PredictionResult | null>;
  /** Clear the current result */
  reset: () => void;
}

export function usePrediction(): UsePredictionReturn {
  const { runPrediction, isReady } = useModel();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(
    async (rgbaData: Uint8Array, imagePath: string): Promise<PredictionResult | null> => {
      if (!isReady) {
        setError('Model is still loading. Please wait.');
        return null;
      }

      setLoading(true);
      setError(null);

      try {
        const prediction = await runPrediction(rgbaData);
        setResult(prediction);

        // Save to local history
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
