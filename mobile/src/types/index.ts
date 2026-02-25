/** Disease detail from the bundled disease_info.json */
export interface Disease {
  crop: string;
  severity: 'None' | 'Moderate' | 'High';
  symptoms: string[];
  treatment: string;
  prevention: string[];
}

/** Map of disease name → Disease detail */
export type DiseaseDatabase = Record<string, Disease>;

/** A single class prediction with name and probability */
export interface ClassPrediction {
  className: string;
  confidence: number;
}

/** Full result returned by the classifier */
export interface PredictionResult {
  disease: string;
  confidence: number;
  crop: string;
  severity: 'None' | 'Moderate' | 'High';
  treatment: string;
  symptoms: string[];
  prevention: string[];
  topK: ClassPrediction[];
}

/** A saved prediction in local history */
export interface HistoryEntry {
  id: string;
  disease: string;
  confidence: number;
  crop: string;
  severity: 'None' | 'Moderate' | 'High';
  treatment: string;
  imagePath: string;
  timestamp: string;
}

/** Crop filter options for disease library */
export type CropFilter = 'All' | 'Corn' | 'Potato' | 'Tomato';

/** Navigation param types */
export type RootStackParamList = {
  MainTabs: { screen?: keyof TabParamList };
  Result: { result: PredictionResult; imagePath: string };
};

export type TabParamList = {
  Home: undefined;
  Scan: undefined;
  History: undefined;
  Library: undefined;
};
