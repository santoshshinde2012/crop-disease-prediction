import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/Ionicons';
import { Gradients, Typography, Spacing, Colors } from '../../theme';

export function HeroSection() {
  const insets = useSafeAreaInsets();

  return (
    <LinearGradient
      colors={[...Gradients.hero]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={[styles.container, { paddingTop: insets.top + Spacing['2xl'] }]}
    >
      <View style={styles.iconContainer}>
        <Icon name="leaf" size={48} color={Colors.accent} />
      </View>
      <Text style={styles.title}>Crop Disease{'\n'}Classifier</Text>
      <Text style={styles.subtitle}>
        AI-powered leaf diagnostics for Tomato, Potato, and Corn — designed for fast, reliable field decisions.
      </Text>
      <View style={styles.statsRow}>
        <View style={styles.stat}>
          <Text style={styles.statValue}>97.8%</Text>
          <Text style={styles.statLabel}>Accuracy</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.stat}>
          <Text style={styles.statValue}>15</Text>
          <Text style={styles.statLabel}>Diseases</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.stat}>
          <Text style={styles.statValue}>{'<1s'}</Text>
          <Text style={styles.statLabel}>Inference</Text>
        </View>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: Spacing['2xl'],
    paddingBottom: Spacing['3xl'],
    borderBottomLeftRadius: 28,
    borderBottomRightRadius: 28,
  },
  iconContainer: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  title: {
    ...Typography.h1,
    fontSize: 32,
    lineHeight: 38,
    color: Colors.textOnDark,
    marginBottom: Spacing.sm,
  },
  subtitle: {
    ...Typography.body,
    color: 'rgba(255, 255, 255, 0.85)',
    marginBottom: Spacing['2xl'],
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    borderRadius: 12,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
  },
  stat: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    ...Typography.h3,
    color: Colors.textOnDark,
    fontWeight: '700',
  },
  statLabel: {
    ...Typography.caption,
    color: 'rgba(255, 255, 255, 0.7)',
    marginTop: 2,
  },
  divider: {
    width: 1,
    height: 30,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
});
