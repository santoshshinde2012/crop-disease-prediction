import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors, Typography, Spacing, Radius } from '../../theme';

interface BadgeProps {
  severity: 'None' | 'Moderate' | 'High';
}

const severityConfig = {
  High: {
    label: 'High Severity',
    bg: Colors.severityHighBg,
    text: Colors.severityHigh,
  },
  Moderate: {
    label: 'Moderate',
    bg: Colors.severityModerateBg,
    text: Colors.severityModerate,
  },
  None: {
    label: 'Healthy',
    bg: Colors.severityNoneBg,
    text: Colors.severityNone,
  },
} as const;

export function Badge({ severity }: BadgeProps) {
  const config = severityConfig[severity];

  return (
    <View style={[styles.badge, { backgroundColor: config.bg }]}>
      <Text style={[styles.text, { color: config.text }]}>{config.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    alignSelf: 'flex-start',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: Radius.full,
  },
  text: {
    ...Typography.caption,
    fontWeight: '600',
  },
});
