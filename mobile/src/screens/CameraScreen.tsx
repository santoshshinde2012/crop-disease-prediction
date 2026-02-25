import React, { useRef, useState, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Platform,
  Linking,
} from 'react-native';
import {
  Camera,
  useCameraDevice,
  useCameraPermission,
} from 'react-native-vision-camera';
import { launchImageLibrary } from 'react-native-image-picker';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import Icon from 'react-native-vector-icons/Ionicons';
import { LoadingOverlay } from '../components/ui/LoadingOverlay';
import { useModel } from '../context/ModelContext';
import { savePrediction } from '../services/storage';
import { preprocessPixels, predict } from '../services/classifier';
import { Colors, Typography, Spacing } from '../theme';
import type { RootStackParamList } from '../types';

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

export function CameraScreen() {
  const navigation = useNavigation<NavigationProp>();
  const camera = useRef<Camera>(null);
  const device = useCameraDevice('back');
  const { hasPermission, requestPermission } = useCameraPermission();
  const { isReady } = useModel();
  const [loading, setLoading] = useState(false);

  const handleCapture = useCallback(async () => {
    if (!camera.current || loading || !isReady) return;
    setLoading(true);

    try {
      const photo = await camera.current.takePhoto({
        qualityPrioritization: 'speed',
      });
      const photoPath = Platform.OS === 'android' ? `file://${photo.path}` : photo.path;

      // In a real app, resize to 224x224 and get RGBA pixel data here.
      // This requires a native module or react-native-image-resizer.
      // For now, we demonstrate the flow:
      const dummyPixels = new Uint8Array(224 * 224 * 4); // placeholder
      const tensor = preprocessPixels(dummyPixels);
      const result = await predict(tensor);

      if (result.confidence < 0.5) {
        Alert.alert(
          'Low Confidence',
          'Could not clearly identify the disease. Try again with better lighting and a closer shot.',
          [{ text: 'OK' }],
        );
      } else {
        await savePrediction(result, photoPath);
        navigation.navigate('Result', { result, imagePath: photoPath });
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to analyze image.';
      Alert.alert('Error', message);
    } finally {
      setLoading(false);
    }
  }, [loading, isReady, navigation]);

  const handleGalleryPick = useCallback(async () => {
    const response = await launchImageLibrary({
      mediaType: 'photo',
      quality: 0.8,
      maxWidth: 1024,
      maxHeight: 1024,
    });

    if (response.didCancel || !response.assets?.[0]?.uri) return;

    setLoading(true);
    try {
      const imagePath = response.assets[0].uri;
      const dummyPixels = new Uint8Array(224 * 224 * 4); // placeholder
      const tensor = preprocessPixels(dummyPixels);
      const result = await predict(tensor);

      await savePrediction(result, imagePath);
      navigation.navigate('Result', { result, imagePath });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to analyze image.';
      Alert.alert('Error', message);
    } finally {
      setLoading(false);
    }
  }, [navigation]);

  // Permission not granted
  if (!hasPermission) {
    return (
      <View style={styles.permissionContainer}>
        <Icon name="camera-outline" size={64} color={Colors.textSecondary} />
        <Text style={styles.permissionTitle}>Camera Access Required</Text>
        <Text style={styles.permissionText}>
          We need camera access to scan leaf images for disease detection.
        </Text>
        <TouchableOpacity
          style={styles.permissionButton}
          onPress={async () => {
            const granted = await requestPermission();
            if (!granted) Linking.openSettings();
          }}
        >
          <Text style={styles.permissionButtonText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // No camera device
  if (!device) {
    return (
      <View style={styles.permissionContainer}>
        <Icon name="camera-outline" size={64} color={Colors.textSecondary} />
        <Text style={styles.permissionTitle}>No Camera Found</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Camera preview */}
      <Camera
        ref={camera}
        device={device}
        isActive={true}
        photo={true}
        style={StyleSheet.absoluteFill}
      />

      {/* Guide overlay */}
      <View style={styles.overlay}>
        {/* Top bar */}
        <View style={styles.topBar}>
          <Text style={styles.instruction}>
            Position the leaf within the circle
          </Text>
        </View>

        {/* Center guide circle */}
        <View style={styles.guideCircle} />

        {/* Bottom controls */}
        <View style={styles.bottomBar}>
          {/* Gallery button */}
          <TouchableOpacity style={styles.sideButton} onPress={handleGalleryPick}>
            <Icon name="images" size={28} color={Colors.textOnDark} />
            <Text style={styles.sideButtonLabel}>Gallery</Text>
          </TouchableOpacity>

          {/* Capture button */}
          <TouchableOpacity
            style={styles.captureButton}
            onPress={handleCapture}
            disabled={loading || !isReady}
            activeOpacity={0.7}
          >
            <View style={styles.captureInner} />
          </TouchableOpacity>

          {/* Model status */}
          <View style={styles.sideButton}>
            <Icon
              name={isReady ? 'checkmark-circle' : 'hourglass'}
              size={28}
              color={isReady ? Colors.accent : Colors.severityModerate}
            />
            <Text style={styles.sideButtonLabel}>
              {isReady ? 'Ready' : 'Loading'}
            </Text>
          </View>
        </View>
      </View>

      <LoadingOverlay visible={loading} message="Analyzing leaf..." />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'space-between',
  },
  topBar: {
    paddingTop: Spacing['5xl'],
    paddingHorizontal: Spacing['2xl'],
    alignItems: 'center',
  },
  instruction: {
    ...Typography.body,
    color: Colors.textOnDark,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm,
    borderRadius: 20,
    overflow: 'hidden',
  },
  guideCircle: {
    width: 260,
    height: 260,
    borderRadius: 130,
    borderWidth: 3,
    borderColor: 'rgba(129, 199, 132, 0.7)',
    borderStyle: 'dashed',
    alignSelf: 'center',
  },
  bottomBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingBottom: Spacing['4xl'],
    paddingHorizontal: Spacing['2xl'],
  },
  sideButton: {
    alignItems: 'center',
    width: 60,
  },
  sideButtonLabel: {
    ...Typography.caption,
    color: Colors.textOnDark,
    marginTop: 4,
  },
  captureButton: {
    width: 76,
    height: 76,
    borderRadius: 38,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureInner: {
    width: 62,
    height: 62,
    borderRadius: 31,
    backgroundColor: Colors.textOnDark,
  },
  // Permission screen
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.background,
    paddingHorizontal: Spacing['3xl'],
    gap: Spacing.lg,
  },
  permissionTitle: {
    ...Typography.h2,
    color: Colors.textPrimary,
    textAlign: 'center',
  },
  permissionText: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  permissionButton: {
    backgroundColor: Colors.primary,
    paddingHorizontal: Spacing['2xl'],
    paddingVertical: Spacing.md,
    borderRadius: 12,
    marginTop: Spacing.lg,
  },
  permissionButtonText: {
    ...Typography.button,
    color: Colors.textOnPrimary,
  },
});
