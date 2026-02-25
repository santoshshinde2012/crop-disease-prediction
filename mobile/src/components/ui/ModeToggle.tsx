import React, { useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';
import { useInferenceMode, InferenceMode } from '../../context/InferenceModeContext';
import { checkApiHealth } from '../../services/apiClient';
import { Colors, Typography, Spacing, Radius, Shadows } from '../../theme';

interface ModeToggleProps {
  /** Use light text/icons for dark backgrounds (e.g. camera overlay) */
  variant?: 'light' | 'dark';
}

export function ModeToggle({ variant = 'dark' }: ModeToggleProps) {
  const { mode, apiBaseUrl, setMode } = useInferenceMode();

  const handlePress = useCallback(
    async (target: InferenceMode) => {
      if (target === mode) return;

      if (target === 'online') {
        const healthy = await checkApiHealth(apiBaseUrl);
        if (!healthy) {
          Alert.alert(
            'API Unavailable',
            `Cannot reach the server at ${apiBaseUrl}. Make sure the REST API is running.\n\nuvicorn api.main:app`,
            [{ text: 'OK' }],
          );
          return;
        }
      }

      setMode(target);
    },
    [mode, apiBaseUrl, setMode],
  );

  const isLight = variant === 'light';
  const inactiveText = isLight ? 'rgba(255,255,255,0.8)' : Colors.textSecondary;
  const inactiveBg = isLight ? 'rgba(255,255,255,0.12)' : 'transparent';
  const containerBg = isLight ? 'rgba(0,0,0,0.35)' : Colors.surfaceMuted;

  return (
    <View style={[styles.container, { backgroundColor: containerBg }, !isLight && styles.containerBorder]}>
      <TouchableOpacity
        style={[
          styles.segment,
          mode === 'offline'
            ? [styles.activeSegment, !isLight && styles.activeSegmentShadow]
            : { backgroundColor: inactiveBg },
        ]}
        onPress={() => handlePress('offline')}
        activeOpacity={0.7}
      >
        <Icon
          name="cloud-offline-outline"
          size={16}
          color={mode === 'offline' ? Colors.textOnPrimary : inactiveText}
        />
        <Text
          style={[
            styles.label,
            { color: mode === 'offline' ? Colors.textOnPrimary : inactiveText },
          ]}
        >
          Offline
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[
          styles.segment,
          mode === 'online'
            ? [styles.activeSegment, !isLight && styles.activeSegmentShadow]
            : { backgroundColor: inactiveBg },
        ]}
        onPress={() => handlePress('online')}
        activeOpacity={0.7}
      >
        <Icon
          name="cloud-outline"
          size={16}
          color={mode === 'online' ? Colors.textOnPrimary : inactiveText}
        />
        <Text
          style={[
            styles.label,
            { color: mode === 'online' ? Colors.textOnPrimary : inactiveText },
          ]}
        >
          Online
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    borderRadius: Radius.full,
    padding: 3,
    alignSelf: 'center',
  },
  containerBorder: {
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
  },
  segment: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.xl,
    paddingVertical: 10,
    borderRadius: Radius.full,
    gap: Spacing.xs,
    minWidth: 100,
    justifyContent: 'center',
  },
  activeSegment: {
    backgroundColor: Colors.primary,
  },
  activeSegmentShadow: {
    ...Shadows.sm,
  },
  label: {
    ...Typography.caption,
    fontWeight: '600',
    fontSize: 13,
  },
});
