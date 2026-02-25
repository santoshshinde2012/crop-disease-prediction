import React, { useRef, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Platform,
  Linking,
  StatusBar,
  Image,
} from 'react-native';
import {
  Camera,
  useCameraDevice,
  useCameraPermission,
} from 'react-native-vision-camera';
import { launchImageLibrary } from 'react-native-image-picker';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/Ionicons';
import { LoadingOverlay } from '../components/ui/LoadingOverlay';
import { Button } from '../components/ui/Button';
import { useModel } from '../context/ModelContext';
import { usePrediction } from '../hooks/usePrediction';
import { CONFIDENCE_THRESHOLD } from '../services/classifier';
import { Colors, Typography, Spacing, Shadows } from '../theme';
import type { RootStackParamList, PredictionResult } from '../types';

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

// Bundled demo image for simulator testing
const demoLeafImage = require('../../assets/images/demo_leaf.png');

export function CameraScreen() {
  const navigation = useNavigation<NavigationProp>();
  const camera = useRef<Camera>(null);
  const device = useCameraDevice('back');
  const { hasPermission, requestPermission } = useCameraPermission();
  const { isReady } = useModel();
  const { loading, analyze } = usePrediction();
  const insets = useSafeAreaInsets();

  const navigateWithResult = useCallback(
    (result: PredictionResult | null, imagePath: string) => {
      if (!result) return;

      if (result.confidence < CONFIDENCE_THRESHOLD) {
        Alert.alert(
          'Low Confidence',
          'Could not clearly identify the disease. Try again with better lighting and a closer shot.',
          [{ text: 'OK' }],
        );
      } else {
        navigation.navigate('Result', { result, imagePath });
      }
    },
    [navigation],
  );

  const handleCapture = useCallback(async () => {
    if (!camera.current || loading || !isReady) return;

    try {
      const photo = await camera.current.takePhoto();
      const photoPath = Platform.OS === 'android' ? `file://${photo.path}` : photo.path;
      const result = await analyze(photoPath);
      navigateWithResult(result, photoPath);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to analyze image.';
      Alert.alert('Error', message);
    }
  }, [loading, isReady, analyze, navigateWithResult]);

  const handleGalleryPick = useCallback(async () => {
    const response = await launchImageLibrary({
      mediaType: 'photo',
      quality: 0.8,
      maxWidth: 1024,
      maxHeight: 1024,
    });

    if (response.didCancel || !response.assets?.[0]?.uri) return;

    try {
      const imagePath = response.assets[0].uri;
      const result = await analyze(imagePath);
      navigateWithResult(result, imagePath);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to analyze image.';
      Alert.alert('Error', message);
    }
  }, [analyze, navigateWithResult]);

  const handleUseDemoImage = useCallback(async () => {
    if (loading || !isReady) return;

    try {
      const imageSource = Image.resolveAssetSource(demoLeafImage);
      const imagePath = imageSource.uri;
      const result = await analyze(imagePath);
      navigateWithResult(result, imagePath);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to analyze demo image.';
      Alert.alert('Error', message);
    }
  }, [loading, isReady, analyze, navigateWithResult]);

  // Permission not granted
  if (!hasPermission) {
    return (
      <View style={[styles.permissionContainer, { paddingTop: insets.top }]}>
        <StatusBar barStyle="dark-content" backgroundColor={Colors.background} />
        <View style={styles.illustrationOuter}>
          <View style={styles.illustrationInner}>
            <Icon name="camera-outline" size={36} color={Colors.primary} />
          </View>
        </View>
        <Text style={styles.permissionTitle}>Camera Access Required</Text>
        <Text style={styles.permissionText}>
          We need camera access to scan leaf images for disease detection.
        </Text>
        <View style={styles.permissionButtons}>
          <Button
            title="Grant Permission"
            onPress={async () => {
              const granted = await requestPermission();
              if (!granted) Linking.openSettings();
            }}
            icon={<Icon name="lock-open-outline" size={20} color={Colors.textOnPrimary} />}
            style={styles.fullWidthButton}
          />
          <Button
            title="Browse Photo Library"
            variant="outline"
            onPress={handleGalleryPick}
            icon={<Icon name="images-outline" size={20} color={Colors.primary} />}
            style={styles.fullWidthButton}
          />
        </View>
      </View>
    );
  }

  // No camera device (e.g. iOS simulator)
  if (!device) {
    return (
      <View style={styles.noDeviceContainer}>
        <StatusBar barStyle="dark-content" backgroundColor={Colors.background} />
        <ScrollView
          contentContainerStyle={[styles.noDeviceScroll, { paddingTop: insets.top + Spacing['3xl'], paddingBottom: insets.bottom + Spacing['3xl'] }]}
          showsVerticalScrollIndicator={false}
          bounces={false}
        >
          {/* Illustration */}
          <View style={styles.illustrationOuter}>
            <View style={styles.illustrationInner}>
              <Icon name="leaf" size={36} color={Colors.primary} />
            </View>
          </View>

          {/* Text */}
          <Text style={styles.noDeviceTitle}>Scan a Leaf</Text>
          <Text style={styles.noDeviceText}>
            No camera detected. You can still analyze leaf images from your photo library or use the
            bundled demo image to try the experience.
          </Text>

          {/* Model status indicator */}
          <View style={styles.modelStatusRow}>
            <Icon
              name={isReady ? 'checkmark-circle' : 'hourglass-outline'}
              size={18}
              color={isReady ? Colors.primaryLight : Colors.severityModerate}
            />
            <Text style={[styles.modelStatusText, { color: isReady ? Colors.primary : Colors.severityModerate }]}>
              {isReady ? 'Model ready' : 'Loading model...'}
            </Text>
          </View>

          {/* Buttons */}
          <View style={styles.noDeviceButtons}>
            <Button
              title="Browse Photo Library"
              onPress={handleGalleryPick}
              icon={<Icon name="images" size={20} color={Colors.textOnPrimary} />}
              style={styles.fullWidthButton}
            />
            <Button
              title="Use Demo Image"
              variant="outline"
              onPress={handleUseDemoImage}
              disabled={!isReady}
              icon={<Icon name="leaf-outline" size={20} color={Colors.primary} />}
              style={styles.fullWidthButton}
            />
          </View>
        </ScrollView>

        <LoadingOverlay visible={loading} message="Analyzing image..." />
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
        <View style={[styles.topBar, { paddingTop: insets.top + Spacing.md }]}>
          <Text style={styles.instruction}>
            Position the leaf within the circle
          </Text>
        </View>

        {/* Center guide circle */}
        <View style={styles.guideCircle} />

        {/* Bottom controls */}
        <View style={[styles.bottomBar, { paddingBottom: insets.bottom + Spacing.xl }]}>
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
  // Shared illustration style
  illustrationOuter: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: Colors.surfaceSubtle,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.xl,
  },
  illustrationInner: {
    width: 68,
    height: 68,
    borderRadius: 34,
    backgroundColor: Colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    ...Shadows.md,
  },
  // Permission screen
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.background,
    paddingHorizontal: Spacing['2xl'],
    paddingBottom: Spacing['4xl'],
  },
  permissionTitle: {
    ...Typography.h1,
    color: Colors.textPrimary,
    textAlign: 'center',
    marginBottom: Spacing.sm,
  },
  permissionText: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginBottom: Spacing['3xl'],
    paddingHorizontal: Spacing.lg,
  },
  permissionButtons: {
    width: '100%',
    gap: Spacing.md,
  },
  // No device (simulator) state
  noDeviceContainer: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  noDeviceScroll: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: Spacing['2xl'],
  },
  noDeviceTitle: {
    ...Typography.h1,
    color: Colors.textPrimary,
    textAlign: 'center',
    marginBottom: Spacing.sm,
  },
  noDeviceText: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.lg,
  },
  modelStatusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.xs,
    marginBottom: Spacing['3xl'],
  },
  modelStatusText: {
    ...Typography.bodySmall,
    fontWeight: '600',
  },
  noDeviceButtons: {
    width: '100%',
    gap: Spacing.md,
    paddingBottom: Spacing.lg,
  },
  fullWidthButton: {
    width: '100%',
  },
});
