import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';
import { Card } from '../ui/Card';
import { Colors, Typography, Spacing } from '../../theme';

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
  color?: string;
}

export function FeatureCard({
  icon,
  title,
  description,
  color = Colors.primary,
}: FeatureCardProps) {
  return (
    <Card style={styles.card}>
      <View style={[styles.iconCircle, { backgroundColor: color + '15' }]}>
        <Icon name={icon} size={24} color={color} />
      </View>
      <View style={styles.content}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.description}>{description}</Text>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.lg,
    marginBottom: Spacing.md,
  },
  iconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
  },
  title: {
    ...Typography.h3,
    fontSize: 16,
    color: Colors.textPrimary,
    marginBottom: 2,
  },
  description: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
});
