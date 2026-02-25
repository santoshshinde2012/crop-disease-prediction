import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ViewStyle,
  ActivityIndicator,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { Colors, Gradients, Typography, Spacing, Radius, Shadows } from '../../theme';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  style?: ViewStyle;
}

export function Button({
  title,
  onPress,
  variant = 'primary',
  loading = false,
  disabled = false,
  icon,
  style,
}: ButtonProps) {
  const isDisabled = disabled || loading;

  if (variant === 'primary') {
    return (
      <TouchableOpacity
        onPress={onPress}
        disabled={isDisabled}
        activeOpacity={0.8}
        style={style}
      >
        <LinearGradient
          colors={isDisabled ? ['#9E9E9E', '#BDBDBD'] : [...Gradients.primary]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={[styles.base, styles.primary]}
        >
          {loading ? (
            <ActivityIndicator color={Colors.textOnPrimary} size="small" />
          ) : (
            <>
              {icon}
              <Text style={[Typography.button, styles.primaryText]}>{title}</Text>
            </>
          )}
        </LinearGradient>
      </TouchableOpacity>
    );
  }

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.7}
      style={[
        styles.base,
        variant === 'secondary' ? styles.secondary : styles.outline,
        isDisabled && styles.disabled,
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator
          color={variant === 'secondary' ? Colors.textOnPrimary : Colors.primary}
          size="small"
        />
      ) : (
        <>
          {icon}
          <Text
            style={[
              Typography.button,
              variant === 'secondary' ? styles.secondaryText : styles.outlineText,
            ]}
          >
            {title}
          </Text>
        </>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing['2xl'],
    borderRadius: Radius.lg,
    gap: Spacing.sm,
    minHeight: 52,
  },
  primary: {
    // gradient handles background
    ...Shadows.lg,
    overflow: 'visible',
  },
  primaryText: {
    color: Colors.textOnPrimary,
  },
  secondary: {
    backgroundColor: Colors.primary,
  },
  secondaryText: {
    color: Colors.textOnPrimary,
  },
  outline: {
    backgroundColor: Colors.transparent,
    borderWidth: 2,
    borderColor: Colors.primary,
  },
  outlineText: {
    color: Colors.primary,
  },
  disabled: {
    opacity: 0.5,
  },
});
