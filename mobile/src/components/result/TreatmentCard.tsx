import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';
import { Card } from '../ui/Card';
import { Colors, Typography, Spacing } from '../../theme';

interface TreatmentCardProps {
  treatment: string;
  isUrgent?: boolean;
}

export function TreatmentCard({ treatment, isUrgent = false }: TreatmentCardProps) {
  return (
    <Card
      style={isUrgent ? { ...styles.card, ...styles.urgentCard } : styles.card}
    >
      <View style={styles.header}>
        <Icon
          name={isUrgent ? 'warning' : 'medkit'}
          size={20}
          color={isUrgent ? Colors.severityHigh : Colors.primary}
        />
        <Text
          style={[
            styles.title,
            isUrgent && styles.urgentTitle,
          ]}
        >
          {isUrgent ? 'Urgent Treatment' : 'Treatment'}
        </Text>
      </View>
      <Text style={styles.text}>{treatment}</Text>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  urgentCard: {
    borderLeftColor: Colors.severityHigh,
    backgroundColor: Colors.severityHighBg,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    marginBottom: Spacing.sm,
  },
  title: {
    ...Typography.h3,
    color: Colors.primaryDark,
  },
  urgentTitle: {
    color: Colors.severityHigh,
  },
  text: {
    ...Typography.body,
    color: Colors.textPrimary,
    lineHeight: 24,
  },
});
