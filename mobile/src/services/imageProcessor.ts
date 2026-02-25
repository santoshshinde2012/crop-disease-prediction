import RNFS from 'react-native-fs';
import ImageResizer from '@bam.tech/react-native-image-resizer';
import { decode as jpegDecode } from 'jpeg-js';

const IMG_SIZE = 224;

/**
 * Resize an image and extract raw RGBA pixel data.
 *
 * Single Responsibility: image I/O only — resize + pixel extraction.
 * The classifier service handles pixel normalization and inference.
 *
 * Pipeline:
 *   1. Resize image to 224x224 using platform-native APIs
 *   2. Read resized JPEG as base64
 *   3. Decode JPEG to raw RGBA pixels using pure-JS decoder
 *
 * @param imagePath - File path or URI to the source image
 * @returns Uint8Array of RGBA pixel data (224 * 224 * 4 = 200,704 bytes)
 */
export async function extractPixels(imagePath: string): Promise<Uint8Array> {
  // Step 1: Resize to model input dimensions using native image APIs
  const resized = await ImageResizer.createResizedImage(
    imagePath,
    IMG_SIZE,
    IMG_SIZE,
    'JPEG',
    100,
    0,
    undefined,
    false,
    { mode: 'stretch' },
  );

  try {
    // Step 2: Read resized image as base64
    const base64 = await RNFS.readFile(resized.uri, 'base64');

    // Step 3: Decode base64 to raw bytes
    const binaryString = atob(base64);
    const jpegBytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      jpegBytes[i] = binaryString.charCodeAt(i);
    }

    // Step 4: Decode JPEG to RGBA pixel data
    const rawImage = jpegDecode(jpegBytes, { useTArray: true, formatAsRGBA: true });

    if (rawImage.width !== IMG_SIZE || rawImage.height !== IMG_SIZE) {
      throw new Error(
        `Unexpected decoded size: ${rawImage.width}x${rawImage.height}, expected ${IMG_SIZE}x${IMG_SIZE}`,
      );
    }

    return rawImage.data as Uint8Array;
  } finally {
    // Clean up temp resized file
    RNFS.unlink(resized.uri).catch(() => {});
  }
}
