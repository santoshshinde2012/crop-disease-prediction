import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
} from 'react-native-reanimated';
import Icon from 'react-native-vector-icons/Ionicons';
import { Badge } from '../ui/Badge';
import { Colors, Typography, Spacing, Radius, Shadows } from '../../theme';
import type { Disease } from '../../types';

interface DiseaseListItemProps {
  name: string;
  disease: Disease;
}

export function DiseaseListItem({ name, disease }: DiseaseListItemProps) {
  const [expanded, setExpanded] = useState(false);
  const rotation = useSharedValue(0);

  const toggleExpand = () => {
    setExpanded((prev) => !prev);
    rotation.value = withTiming(expanded ? 0 : 180, { duration: 250 });
  };

  const chevronStyle = useAnimatedStyle(() => ({
    transform: [{ rotate: `${rotation.value}deg` }],
  }));

  const displayName = name.includes(': ') ? name.split(': ')[1] : name;

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.header}
        onPress={toggleExpand}
        activeOpacity={0.7}
      >
        <View style={styles.headerLeft}>
          <Text style={styles.name}>{displayName}</Text>
          <Badge severity={disease.severity} />
        </View>
        <Animated.View style={chevronStyle}>
          <Icon name="chevron-down" size={20} color={Colors.textSecondary} />
        </Animated.View>
      </TouchableOpacity>

      {expanded && (
        <View style={styles.body}>
          {/* Symptoms */}
          <Text style={styles.sectionTitle}>Symptoms</Text>
          {disease.symptoms.map((s, i) => (
            <View key={i} style={styles.listItem}>
              <Icon name="alert-circle-outline" size={16} color={Colors.severityModerate} />
              <Text style={styles.listText}>{s}</Text>
            </View>
          ))}

          {/* Treatment */}
          <Text style={styles.sectionTitle}>Treatment</Text>
          <Text style={styles.treatmentText}>{disease.treatment}</Text>

          {/* Prevention */}
          <Text style={styles.sectionTitle}>Prevention</Text>
          {disease.prevention.map((p, i) => (
            <View key={i} style={styles.listItem}>
              <Icon name="checkmark-circle-outline" size={16} color={Colors.primary} />
              <Text style={styles.listText}>{p}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.surface,
    borderRadius: Radius.md,
    marginBottom: Spacing.md,
    ...Shadows.sm,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: Spacing.lg,
  },
  headerLeft: {
    flex: 1,
    gap: Spacing.sm,
  },
  name: {
    ...Typography.h3,
    color: Colors.textPrimary,
  },
  body: {
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.lg,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    paddingTop: Spacing.md,
  },
  sectionTitle: {
    ...Typography.caption,
    color: Colors.primary,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginTop: Spacing.md,
    marginBottom: Spacing.sm,
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: Spacing.sm,
    marginBottom: Spacing.sm,
  },
  listText: {
    ...Typography.bodySmall,
    color: Colors.textPrimary,
    flex: 1,
  },
  treatmentText: {
    ...Typography.body,
    color: Colors.textPrimary,
    paddingLeft: Spacing.xs,
  },
});
