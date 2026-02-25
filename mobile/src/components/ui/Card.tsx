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
    // Slightly larger radius for a more modern, premium feel
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    backgroundColor: Colors.surface,
  },
});

const variantStyles = StyleSheet.create({
  elevated: {
    ...Shadows.md,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.borderLight,
  },
  outlined: {
    borderWidth: 1,
    borderColor: Colors.borderLight,
  },
  filled: {
    backgroundColor: Colors.surfaceSubtle,
  },
});
