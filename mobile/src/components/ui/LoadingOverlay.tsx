import React from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { Colors, Typography, Spacing } from '../../theme';

interface LoadingOverlayProps {
  message?: string;
  visible: boolean;
}

export function LoadingOverlay({
  message = 'Analyzing...',
  visible,
}: LoadingOverlayProps) {
  if (!visible) return null;

  return (
    <View style={styles.overlay}>
      <View style={styles.box}>
        <ActivityIndicator size="large" color={Colors.primary} />
        <Text style={styles.message}>{message}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: Colors.overlay,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 100,
  },
  box: {
    backgroundColor: Colors.surface,
    borderRadius: 16,
    padding: Spacing['3xl'],
    alignItems: 'center',
    gap: Spacing.lg,
    minWidth: 180,
  },
  message: {
    ...Typography.body,
    color: Colors.textPrimary,
  },
});
