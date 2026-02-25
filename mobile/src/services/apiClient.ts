import diseaseInfo from '../../assets/data/disease_info.json';
import type { PredictionResult, ClassPrediction, DiseaseDatabase } from '../types';

const diseases = diseaseInfo as DiseaseDatabase;

interface ApiTopK {
  class_name: string;
  confidence: number;
}

interface ApiPredictionResponse {
  success: boolean;
  prediction: string;
  confidence: number;
  crop: string;
  severity: string;
  treatment: string;
  top_k: ApiTopK[];
}

/**
 * Send an image to the REST API for prediction.
 *
 * Uses fetch + FormData (React Native's built-in networking).
 * Maps the API response to the app's PredictionResult type,
 * filling symptoms/prevention from the bundled disease_info.json.
 */
export async function predictOnline(
  imagePath: string,
  apiBaseUrl: string,
): Promise<PredictionResult> {
  // Build multipart form data with the image file
  const formData = new FormData();
  formData.append('file', {
    uri: imagePath,
    type: 'image/jpeg',
    name: 'leaf.jpg',
  } as unknown as Blob);

  const response = await fetch(`${apiBaseUrl}/api/v1/predict`, {
    method: 'POST',
    body: formData,
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => '');
    throw new Error(
      response.status === 503
        ? 'API model not loaded. Please wait and try again.'
        : `API error (${response.status}): ${errorText || 'Unknown error'}`,
    );
  }

  const data: ApiPredictionResponse = await response.json();

  if (!data.success) {
    throw new Error('API returned unsuccessful response.');
  }

  // Map API response to PredictionResult
  const diseaseName = data.prediction;
  const details = diseases[diseaseName];

  const topK: ClassPrediction[] = data.top_k.map((item) => ({
    className: item.class_name,
    confidence: item.confidence,
  }));

  return {
    disease: diseaseName,
    confidence: data.confidence,
    crop: data.crop,
    severity: (details?.severity ?? data.severity) as PredictionResult['severity'],
    treatment: data.treatment,
    symptoms: details?.symptoms ?? [],
    prevention: details?.prevention ?? [],
    topK,
  };
}

/**
 * Check if the REST API is reachable and healthy.
 */
export async function checkApiHealth(apiBaseUrl: string): Promise<boolean> {
  try {
    const response = await fetch(`${apiBaseUrl}/api/v1/health`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    return response.ok;
  } catch {
    return false;
  }
}
