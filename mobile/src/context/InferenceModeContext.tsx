import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type InferenceMode = 'offline' | 'online';

const STORAGE_KEY = '@inference_mode';
const DEFAULT_API_URL = Platform.OS === 'android'
  ? 'http://10.0.2.2:8000'  // Android emulator → host machine
  : 'http://localhost:8000';

interface InferenceModeContextValue {
  mode: InferenceMode;
  apiBaseUrl: string;
  setMode: (mode: InferenceMode) => void;
}

const InferenceModeContext = createContext<InferenceModeContextValue | null>(null);

export function InferenceModeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setModeState] = useState<InferenceMode>('offline');

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY).then((stored) => {
      if (stored === 'online' || stored === 'offline') {
        setModeState(stored);
      }
    });
  }, []);

  const setMode = useCallback((newMode: InferenceMode) => {
    setModeState(newMode);
    AsyncStorage.setItem(STORAGE_KEY, newMode);
  }, []);

  return (
    <InferenceModeContext.Provider value={{ mode, apiBaseUrl: DEFAULT_API_URL, setMode }}>
      {children}
    </InferenceModeContext.Provider>
  );
}

export function useInferenceMode(): InferenceModeContextValue {
  const ctx = useContext(InferenceModeContext);
  if (!ctx) throw new Error('useInferenceMode must be used within InferenceModeProvider');
  return ctx;
}
