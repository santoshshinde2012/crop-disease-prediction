import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';
import { Card } from '../ui/Card';
import { Colors, Typography, Spacing } from '../../theme';

interface PreventionListProps {
  title: string;
  items: string[];
  icon?: string;
  iconColor?: string;
}

export function PreventionList({
  title,
  items,
  icon = 'checkmark-circle',
  iconColor = Colors.primary,
}: PreventionListProps) {
  if (items.length === 0) return null;

  return (
    <Card>
      <View style={styles.header}>
        <Icon name="shield-checkmark" size={20} color={Colors.primary} />
        <Text style={styles.title}>{title}</Text>
      </View>
      {items.map((item, index) => (
        <View key={index} style={styles.item}>
          <Icon name={icon} size={18} color={iconColor} style={styles.itemIcon} />
          <Text style={styles.itemText}>{item}</Text>
        </View>
      ))}
    </Card>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    marginBottom: Spacing.md,
  },
  title: {
    ...Typography.h3,
    color: Colors.primaryDark,
  },
  item: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: Spacing.sm,
    marginBottom: Spacing.sm,
    paddingLeft: Spacing.xs,
  },
  itemIcon: {
    marginTop: 2,
  },
  itemText: {
    ...Typography.body,
    color: Colors.textPrimary,
    flex: 1,
    lineHeight: 22,
  },
});
