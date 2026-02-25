import AsyncStorage from '@react-native-async-storage/async-storage';
import type { HistoryEntry, PredictionResult } from '../types';

const HISTORY_KEY = '@crop_disease/history';
const MAX_HISTORY = 50;

/** Save a prediction to local history */
export async function savePrediction(
  result: PredictionResult,
  imagePath: string,
): Promise<HistoryEntry> {
  const entry: HistoryEntry = {
    id: Date.now().toString(),
    disease: result.disease,
    confidence: result.confidence,
    crop: result.crop,
    severity: result.severity,
    treatment: result.treatment,
    imagePath,
    timestamp: new Date().toISOString(),
  };

  const history = await getHistory();
  history.unshift(entry);

  // Keep only the most recent entries
  const trimmed = history.slice(0, MAX_HISTORY);
  await AsyncStorage.setItem(HISTORY_KEY, JSON.stringify(trimmed));

  return entry;
}

/** Retrieve all saved predictions, newest first */
export async function getHistory(): Promise<HistoryEntry[]> {
  const raw = await AsyncStorage.getItem(HISTORY_KEY);
  if (!raw) return [];

  try {
    return JSON.parse(raw) as HistoryEntry[];
  } catch {
    return [];
  }
}

/** Delete a single entry by ID */
export async function deleteEntry(id: string): Promise<void> {
  const history = await getHistory();
  const filtered = history.filter((entry) => entry.id !== id);
  await AsyncStorage.setItem(HISTORY_KEY, JSON.stringify(filtered));
}

/** Clear all prediction history */
export async function clearHistory(): Promise<void> {
  await AsyncStorage.removeItem(HISTORY_KEY);
}
