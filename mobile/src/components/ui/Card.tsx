import React from 'react';
import { View, ViewStyle, StyleSheet } from 'react-native';
import { Colors, Radius, Shadows, Spacing } from '../../theme';

interface CardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  variant?: 'elevated' | 'outlined' | 'filled';
}

export function Card({ children, style, variant = 'elevated' }: CardProps) {
  return (
    <View style={[styles.base, variantStyles[variant], style]}>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: Radius.md,
    padding: Spacing.lg,
    backgroundColor: Colors.surface,
  },
});

const variantStyles = StyleSheet.create({
  elevated: {
    ...Shadows.md,
  },
  outlined: {
    borderWidth: 1,
    borderColor: Colors.border,
  },
  filled: {
    backgroundColor: Colors.surfaceSubtle,
  },
});
