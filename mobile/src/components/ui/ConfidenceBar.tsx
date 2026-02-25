import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  Easing,
} from 'react-native-reanimated';
import { Colors, Typography, Spacing, Radius } from '../../theme';

interface ConfidenceBarProps {
  label: string;
  confidence: number;
  isTop?: boolean;
}

function getBarColor(confidence: number, isTop: boolean): string {
  if (isTop) return Colors.barFillHigh;
  if (confidence > 0.3) return Colors.barFillMedium;
  return Colors.barFillLow;
}

export function ConfidenceBar({ label, confidence, isTop = false }: ConfidenceBarProps) {
  const widthPercent = useSharedValue(0);

  useEffect(() => {
    widthPercent.value = withTiming(confidence * 100, {
      duration: 800,
      easing: Easing.out(Easing.cubic),
    });
  }, [confidence, widthPercent]);

  const animatedStyle = useAnimatedStyle(() => ({
    width: `${widthPercent.value}%`,
  }));

  const barColor = getBarColor(confidence, isTop);
  const percent = (confidence * 100).toFixed(1);

  return (
    <View style={styles.container}>
      <View style={styles.labelRow}>
        <Text
          style={[styles.label, isTop && styles.labelBold]}
          numberOfLines={1}
        >
          {label}
        </Text>
        <Text style={[styles.percent, isTop && styles.percentBold]}>
          {percent}%
        </Text>
      </View>
      <View style={styles.track}>
        <Animated.View
          style={[styles.fill, { backgroundColor: barColor }, animatedStyle]}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: Spacing.sm,
  },
  labelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  label: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    flex: 1,
    marginRight: Spacing.sm,
  },
  labelBold: {
    color: Colors.textPrimary,
    fontWeight: '600',
  },
  percent: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
  percentBold: {
    color: Colors.primaryDark,
    fontWeight: '700',
  },
  track: {
    height: 8,
    backgroundColor: Colors.barTrack,
    borderRadius: Radius.sm,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    borderRadius: Radius.sm,
  },
});
