import { useState, useCallback } from 'react';
import { useModel } from '../context/ModelContext';
import { useInferenceMode } from '../context/InferenceModeContext';
import { extractPixels } from '../services/imageProcessor';
import { predictOnline } from '../services/apiClient';
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
 * Supports two inference modes:
 *   - offline: imageProcessor → TFLite on-device inference → save
 *   - online:  send image to REST API → save
 */
export function usePrediction(): UsePredictionReturn {
  const { runPrediction, isReady } = useModel();
  const { mode, apiBaseUrl } = useInferenceMode();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(
    async (imagePath: string): Promise<PredictionResult | null> => {
      if (mode === 'offline' && !isReady) {
        setError('Model is still loading. Please wait.');
        return null;
      }

      setLoading(true);
      setError(null);

      try {
        let prediction: PredictionResult;

        if (mode === 'online') {
          prediction = await predictOnline(imagePath, apiBaseUrl);
        } else {
          const rgbaPixels = await extractPixels(imagePath);
          prediction = await runPrediction(rgbaPixels);
        }

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
    [mode, apiBaseUrl, runPrediction, isReady],
  );

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { loading, result, error, analyze, reset };
}
