import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { Badge } from '../ui/Badge';
import { Colors, Typography, Spacing, Radius, Shadows } from '../../theme';
import type { PredictionResult } from '../../types';

interface DiagnosisCardProps {
  result: PredictionResult;
  imagePath: string;
}

export function DiagnosisCard({ result, imagePath }: DiagnosisCardProps) {
  const confidencePercent = (result.confidence * 100).toFixed(1);
  const isHealthy = result.severity === 'None';
  const displayName = isHealthy
    ? 'Healthy'
    : result.disease.split(': ')[1] || result.disease;
  const severityColor = isHealthy
    ? Colors.severityNone
    : result.severity === 'High'
      ? Colors.severityHigh
      : Colors.severityModerate;

  return (
    <View style={styles.container}>
      {/* Image hero with gradient overlay */}
      <View style={styles.imageWrapper}>
        <Image
          source={{ uri: imagePath }}
          style={StyleSheet.absoluteFill}
          resizeMode="cover"
        />
        <LinearGradient
          colors={['transparent', 'rgba(0,0,0,0.65)']}
          style={StyleSheet.absoluteFill}
        />
        <View style={styles.imageContent}>
          <Text style={styles.cropLabel}>{result.crop}</Text>
          <Text style={styles.diseaseName}>{displayName}</Text>
          <Badge severity={result.severity} />
        </View>
      </View>

      {/* Quick stats row */}
      <View style={styles.statsRow}>
        <View style={styles.stat}>
          <Text style={[styles.statValue, { color: Colors.primaryDark }]}>
            {confidencePercent}%
          </Text>
          <Text style={styles.statLabel}>Confidence</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.stat}>
          <Text style={[styles.statValue, { color: severityColor }]}>
            {isHealthy ? 'Healthy' : result.severity}
          </Text>
          <Text style={styles.statLabel}>Severity</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.stat}>
          <Text style={styles.statValue}>{result.crop}</Text>
          <Text style={styles.statLabel}>Crop</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.surface,
    borderRadius: Radius.lg,
    overflow: 'hidden',
    ...Shadows.md,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.borderLight,
  },
  imageWrapper: {
    height: 240,
    justifyContent: 'flex-end',
  },
  imageContent: {
    padding: Spacing.lg,
    gap: Spacing.xs,
  },
  cropLabel: {
    ...Typography.caption,
    color: 'rgba(255,255,255,0.85)',
    textTransform: 'uppercase',
    letterSpacing: 1.5,
    fontWeight: '700',
  },
  diseaseName: {
    ...Typography.h1,
    color: Colors.textOnDark,
    fontSize: 26,
    lineHeight: 32,
  },
  statsRow: {
    flexDirection: 'row',
    paddingVertical: Spacing.lg,
    paddingHorizontal: Spacing.md,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: Colors.borderLight,
  },
  stat: {
    flex: 1,
    alignItems: 'center',
    gap: 2,
  },
  statValue: {
    ...Typography.h3,
    fontWeight: '700',
    color: Colors.textPrimary,
    fontSize: 17,
  },
  statLabel: {
    ...Typography.caption,
    color: Colors.textSecondary,
  },
  statDivider: {
    width: 1,
    height: 36,
    backgroundColor: Colors.border,
    alignSelf: 'center',
  },
});
