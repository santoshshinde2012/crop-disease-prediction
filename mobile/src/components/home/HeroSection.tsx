import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/Ionicons';
import { ModeToggle } from '../ui/ModeToggle';
import { Gradients, Typography, Spacing, Colors } from '../../theme';

export function HeroSection() {
  const insets = useSafeAreaInsets();

  return (
    <View style={styles.outer}>
      {/* Gradient background — never drives layout */}
      <LinearGradient
        colors={[...Gradients.hero]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={StyleSheet.absoluteFill}
      />

      {/* Content */}
      <View style={[styles.content, { paddingTop: insets.top + Spacing.xl }]}>
        <View style={styles.iconContainer}>
          <Icon name="leaf" size={32} color={Colors.accent} />
        </View>
        <Text style={styles.title}>Crop Disease{'\n'}Classifier</Text>
        <Text style={styles.subtitle}>
          AI-powered leaf diagnostics for Tomato, Potato, and Corn.
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
        <View style={styles.toggleRow}>
          <ModeToggle variant="light" />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  outer: {
    overflow: 'hidden',
    borderBottomLeftRadius: 32,
    borderBottomRightRadius: 32,
  },
  content: {
    paddingHorizontal: Spacing['2xl'],
    paddingBottom: Spacing.xl,
  },
  iconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  title: {
    ...Typography.h1,
    fontSize: 32,
    lineHeight: 38,
    color: Colors.textOnDark,
    marginBottom: Spacing.xs,
  },
  subtitle: {
    ...Typography.body,
    color: 'rgba(255, 255, 255, 0.85)',
    lineHeight: 22,
    marginBottom: Spacing.lg,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    borderRadius: Spacing.md,
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
    fontSize: 20,
  },
  statLabel: {
    ...Typography.caption,
    color: 'rgba(255, 255, 255, 0.7)',
    marginTop: 2,
  },
  toggleRow: {
    alignItems: 'center',
    marginTop: Spacing.lg,
  },
  divider: {
    width: 1,
    height: 32,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
});
