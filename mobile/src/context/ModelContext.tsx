import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { loadModel, predict, preprocessPixels, releaseModel } from '../services/classifier';
import type { PredictionResult } from '../types';

interface ModelContextValue {
  /** Whether the ONNX model is loaded and ready */
  isReady: boolean;
  /** Error message if model failed to load */
  error: string | null;
  /** Run prediction on RGBA pixel data (224x224) */
  runPrediction: (rgbaData: Uint8Array) => Promise<PredictionResult>;
}

const ModelContext = createContext<ModelContextValue | null>(null);

export function ModelProvider({ children }: { children: React.ReactNode }) {
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    loadModel()
      .then(() => {
        if (mounted) setIsReady(true);
      })
      .catch((err: Error) => {
        if (mounted) setError(err.message);
      });

    return () => {
      mounted = false;
      releaseModel();
    };
  }, []);

  const runPrediction = useCallback(
    async (rgbaData: Uint8Array): Promise<PredictionResult> => {
      if (!isReady) throw new Error('Model is not ready yet.');
      const tensor = preprocessPixels(rgbaData);
      return predict(tensor);
    },
    [isReady],
  );

  return (
    <ModelContext.Provider value={{ isReady, error, runPrediction }}>
      {children}
    </ModelContext.Provider>
  );
}

/** Access the model context. Must be used within ModelProvider. */
export function useModel(): ModelContextValue {
  const ctx = useContext(ModelContext);
  if (!ctx) throw new Error('useModel must be used within a ModelProvider');
  return ctx;
}
