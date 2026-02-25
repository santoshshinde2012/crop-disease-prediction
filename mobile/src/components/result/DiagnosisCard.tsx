import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Colors, Typography, Spacing } from '../../theme';
import type { PredictionResult } from '../../types';

interface DiagnosisCardProps {
  result: PredictionResult;
  imagePath: string;
}

export function DiagnosisCard({ result, imagePath }: DiagnosisCardProps) {
  const confidencePercent = (result.confidence * 100).toFixed(1);
  const isHealthy = result.severity === 'None';

  return (
    <Card style={styles.card}>
      {/* Leaf image thumbnail */}
      <Image source={{ uri: imagePath }} style={styles.image} />

      <View style={styles.content}>
        {/* Crop label */}
        <Text style={styles.cropLabel}>{result.crop}</Text>

        {/* Disease name */}
        <Text style={styles.diseaseName}>
          {isHealthy ? 'Healthy' : result.disease.split(': ')[1] || result.disease}
        </Text>

        {/* Severity badge */}
        <Badge severity={result.severity} />

        {/* Confidence */}
        <View style={styles.confidenceRow}>
          <Text style={styles.confidenceValue}>{confidencePercent}%</Text>
          <Text style={styles.confidenceLabel}>confidence</Text>
        </View>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 0,
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: 200,
    resizeMode: 'cover',
  },
  content: {
    padding: Spacing.lg,
    gap: Spacing.sm,
  },
  cropLabel: {
    ...Typography.caption,
    color: Colors.primary,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  diseaseName: {
    ...Typography.h2,
    color: Colors.textPrimary,
  },
  confidenceRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: Spacing.sm,
    marginTop: Spacing.xs,
  },
  confidenceValue: {
    ...Typography.display,
    color: Colors.primaryDark,
  },
  confidenceLabel: {
    ...Typography.body,
    color: Colors.textSecondary,
  },
});
