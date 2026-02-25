import React from 'react';
import {
  TouchableOpacity,
  Text,
  View,
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
  size?: 'default' | 'large';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  style?: ViewStyle;
}

export function Button({
  title,
  onPress,
  variant = 'primary',
  size = 'default',
  loading = false,
  disabled = false,
  icon,
  style,
}: ButtonProps) {
  const isDisabled = disabled || loading;
  const isLarge = size === 'large';

  if (variant === 'primary') {
    return (
      <View style={[styles.shadowWrapper, isLarge && styles.shadowWrapperLarge, style]}>
        <TouchableOpacity
          onPress={onPress}
          disabled={isDisabled}
          activeOpacity={0.8}
          style={[styles.touchable, isLarge && styles.touchableLarge]}
        >
          <LinearGradient
            colors={isDisabled ? ['#9E9E9E', '#BDBDBD'] : [...Gradients.primary]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={[styles.base, isLarge && styles.baseLarge]}
          >
            {loading ? (
              <ActivityIndicator color={Colors.textOnPrimary} size="small" />
            ) : (
              <>
                {icon}
                <Text style={[Typography.button, styles.primaryText, isLarge && styles.textLarge]}>
                  {title}
                </Text>
              </>
            )}
          </LinearGradient>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.7}
      style={[
        styles.base,
        isLarge && styles.baseLarge,
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
              isLarge && styles.textLarge,
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
  shadowWrapper: {
    borderRadius: Radius.lg,
    ...Shadows.lg,
  },
  shadowWrapperLarge: {
    borderRadius: Radius.xl,
  },
  touchable: {
    borderRadius: Radius.lg,
    overflow: 'hidden',
  },
  touchableLarge: {
    borderRadius: Radius.xl,
  },
  base: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    paddingHorizontal: Spacing['2xl'],
    borderRadius: Radius.lg,
    gap: Spacing.sm,
    minHeight: 54,
  },
  baseLarge: {
    paddingVertical: Spacing.lg,
    minHeight: 58,
    borderRadius: Radius.xl,
  },
  primaryText: {
    color: Colors.textOnPrimary,
  },
  textLarge: {
    fontSize: 17,
  },
  secondary: {
    backgroundColor: Colors.primary,
  },
  secondaryText: {
    color: Colors.textOnPrimary,
  },
  outline: {
    backgroundColor: Colors.surface,
    borderWidth: 1.5,
    borderColor: Colors.primary,
  },
  outlineText: {
    color: Colors.primary,
  },
  disabled: {
    opacity: 0.5,
  },
});
