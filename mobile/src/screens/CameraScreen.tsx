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
import { ModeToggle } from '../components/ui/ModeToggle';
import { useModel } from '../context/ModelContext';
import { useInferenceMode } from '../context/InferenceModeContext';
import { usePrediction } from '../hooks/usePrediction';
import { CONFIDENCE_THRESHOLD } from '../services/classifier';
import { Colors, Typography, Spacing, Radius, Shadows } from '../theme';
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
  const { mode } = useInferenceMode();
  const { loading, analyze } = usePrediction();
  const insets = useSafeAreaInsets();
  const canInfer = mode === 'online' || isReady;

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
    if (!camera.current || loading || !canInfer) return;

    try {
      const photo = await camera.current.takePhoto();
      const photoPath = Platform.OS === 'android' ? `file://${photo.path}` : photo.path;
      const result = await analyze(photoPath);
      navigateWithResult(result, photoPath);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to analyze image.';
      Alert.alert('Error', message);
    }
  }, [loading, canInfer, analyze, navigateWithResult]);

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
    if (loading || !canInfer) return;

    try {
      const imageSource = Image.resolveAssetSource(demoLeafImage);
      const imagePath = imageSource.uri;
      const result = await analyze(imagePath);
      navigateWithResult(result, imagePath);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to analyze demo image.';
      Alert.alert('Error', message);
    }
  }, [loading, canInfer, analyze, navigateWithResult]);

  // Permission not granted
  if (!hasPermission) {
    return (
      <View style={[styles.permissionContainer, { paddingTop: insets.top }]}>
        <StatusBar barStyle="dark-content" backgroundColor={Colors.background} />
        <View style={styles.illustrationOuter}>
          <View style={styles.illustrationInner}>
            <Icon name="camera-outline" size={40} color={Colors.primary} />
          </View>
        </View>
        <Text style={styles.permissionTitle}>Camera Access Required</Text>
        <Text style={styles.permissionText}>
          We need camera access to scan leaf images for disease detection.
        </Text>
        <View style={styles.permissionButtons}>
          <Button
            title="Grant Permission"
            size="large"
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
            size="large"
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
          contentContainerStyle={[
            styles.noDeviceScroll,
            { paddingTop: insets.top + Spacing['3xl'], paddingBottom: insets.bottom + Spacing['5xl'] },
          ]}
          showsVerticalScrollIndicator={false}
          bounces={false}
        >
          {/* Illustration */}
          <View style={styles.illustrationOuter}>
            <View style={styles.illustrationInner}>
              <Icon name="leaf" size={40} color={Colors.primary} />
            </View>
          </View>

          {/* Text */}
          <Text style={styles.noDeviceTitle}>Scan a Leaf</Text>
          <Text style={styles.noDeviceText}>
            No camera detected. You can still analyze leaf images from your photo library or use the
            bundled demo image to try the experience.
          </Text>

          {/* Toggle + Status Card */}
          <View style={styles.statusCard}>
            <ModeToggle />
            <View style={styles.statusDivider} />
            <View style={styles.modelStatusRow}>
              <View style={[styles.statusDot, { backgroundColor: canInfer ? Colors.primaryLight : Colors.severityModerate }]} />
              <Text style={[styles.modelStatusText, { color: canInfer ? Colors.primary : Colors.severityModerate }]}>
                {mode === 'online' ? 'API mode — predictions via REST API' : isReady ? 'Model ready — on-device inference' : 'Loading model...'}
              </Text>
            </View>
          </View>

          {/* Buttons */}
          <View style={styles.noDeviceButtons}>
            <Button
              title="Browse Photo Library"
              size="large"
              onPress={handleGalleryPick}
              icon={<Icon name="images" size={22} color={Colors.textOnPrimary} />}
              style={styles.fullWidthButton}
            />
            <Button
              title="Use Demo Image"
              variant="outline"
              size="large"
              onPress={handleUseDemoImage}
              disabled={!canInfer}
              icon={<Icon name="leaf-outline" size={22} color={Colors.primary} />}
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
          <ModeToggle variant="light" />
          <Text style={styles.instruction}>
            Position the leaf within the circle
          </Text>
        </View>

        {/* Center guide circle */}
        <View style={styles.guideCircle} />

        {/* Bottom controls */}
        <View style={[styles.bottomBar, { paddingBottom: insets.bottom + Spacing.xl }]}>
          {/* Gallery button */}
          <TouchableOpacity style={styles.sideButton} onPress={handleGalleryPick} activeOpacity={0.7}>
            <View style={styles.sideButtonIcon}>
              <Icon name="images" size={24} color={Colors.textOnDark} />
            </View>
            <Text style={styles.sideButtonLabel}>Gallery</Text>
          </TouchableOpacity>

          {/* Capture button */}
          <TouchableOpacity
            style={[styles.captureButton, (!canInfer || loading) && styles.captureButtonDisabled]}
            onPress={handleCapture}
            disabled={loading || !canInfer}
            activeOpacity={0.7}
          >
            <View style={styles.captureInner} />
          </TouchableOpacity>

          {/* Model status */}
          <View style={styles.sideButton}>
            <View style={styles.sideButtonIcon}>
              <Icon
                name={canInfer ? 'checkmark-circle' : 'hourglass'}
                size={24}
                color={canInfer ? Colors.accent : Colors.severityModerate}
              />
            </View>
            <Text style={styles.sideButtonLabel}>
              {mode === 'online' ? 'API' : isReady ? 'Ready' : 'Loading'}
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
    gap: Spacing.sm,
  },
  instruction: {
    ...Typography.bodySmall,
    color: Colors.textOnDark,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm,
    borderRadius: Radius.full,
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
    justifyContent: 'space-evenly',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
  },
  sideButton: {
    alignItems: 'center',
    width: 70,
    gap: 6,
  },
  sideButtonIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(255,255,255,0.15)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  sideButtonLabel: {
    ...Typography.caption,
    color: Colors.textOnDark,
  },
  captureButton: {
    width: 84,
    height: 84,
    borderRadius: 42,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    borderColor: 'rgba(255, 255, 255, 0.6)',
  },
  captureButtonDisabled: {
    opacity: 0.4,
  },
  captureInner: {
    width: 66,
    height: 66,
    borderRadius: 33,
    backgroundColor: Colors.textOnDark,
  },
  // Shared illustration style
  illustrationOuter: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: Colors.surfaceSubtle,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.xl,
  },
  illustrationInner: {
    width: 80,
    height: 80,
    borderRadius: 40,
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
    paddingHorizontal: Spacing['3xl'],
    paddingBottom: Spacing['4xl'],
  },
  permissionTitle: {
    ...Typography.h2,
    color: Colors.textPrimary,
    textAlign: 'center',
    marginBottom: Spacing.sm,
  },
  permissionText: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginBottom: Spacing['3xl'],
    paddingHorizontal: Spacing.md,
    lineHeight: 24,
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
    alignItems: 'center',
    paddingHorizontal: Spacing['2xl'],
  },
  noDeviceTitle: {
    ...Typography.h2,
    color: Colors.textPrimary,
    textAlign: 'center',
    marginBottom: Spacing.sm,
  },
  noDeviceText: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    paddingHorizontal: Spacing.sm,
    marginBottom: Spacing['2xl'],
    lineHeight: 24,
  },
  statusCard: {
    width: '100%',
    backgroundColor: Colors.surface,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    alignItems: 'center',
    gap: Spacing.md,
    marginBottom: Spacing['3xl'],
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.borderLight,
    ...Shadows.sm,
  },
  statusDivider: {
    width: '100%',
    height: StyleSheet.hairlineWidth,
    backgroundColor: Colors.border,
  },
  modelStatusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  modelStatusText: {
    ...Typography.bodySmall,
    fontWeight: '500',
  },
  noDeviceButtons: {
    width: '100%',
    gap: Spacing.md,
  },
  fullWidthButton: {
    width: '100%',
  },
});
