import React, { useState, useMemo } from 'react';
import {
  View,
  Text,
  SectionList,
  TouchableOpacity,
  StyleSheet,
  StatusBar,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/Ionicons';
import { DiseaseListItem } from '../components/library/DiseaseListItem';
import diseaseData from '../../assets/data/disease_info.json';
import { Colors, Typography, Spacing, Radius } from '../theme';
import type { CropFilter, Disease, DiseaseDatabase } from '../types';

const diseases = diseaseData as DiseaseDatabase;
const FILTERS: CropFilter[] = ['All', 'Corn', 'Potato', 'Tomato'];

interface Section {
  title: string;
  data: { name: string; disease: Disease }[];
}

export function DiseaseLibraryScreen() {
  const insets = useSafeAreaInsets();
  const [filter, setFilter] = useState<CropFilter>('All');

  const sections = useMemo((): Section[] => {
    const grouped: Record<string, { name: string; disease: Disease }[]> = {};

    Object.entries(diseases).forEach(([name, disease]) => {
      if (filter !== 'All' && disease.crop !== filter) return;

      const crop = disease.crop;
      if (!grouped[crop]) grouped[crop] = [];
      grouped[crop].push({ name, disease });
    });

    return Object.entries(grouped)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([title, data]) => ({ title, data }));
  }, [filter]);

  const totalCount = sections.reduce((sum, s) => sum + s.data.length, 0);

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={Colors.background} />

      {/* Header */}
      <View style={[styles.header, { paddingTop: insets.top + Spacing.lg }]}>
        <Text style={styles.title}>Disease Library</Text>
        <Text style={styles.subtitle}>{totalCount} diseases</Text>
      </View>

      {/* Filter tabs */}
      <View style={styles.filterRow}>
        {FILTERS.map((f) => (
          <TouchableOpacity
            key={f}
            style={[styles.filterTab, filter === f && styles.filterTabActive]}
            onPress={() => setFilter(f)}
            activeOpacity={0.7}
          >
            <Text
              style={[
                styles.filterText,
                filter === f && styles.filterTextActive,
              ]}
            >
              {f}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Disease list */}
      <SectionList
        sections={sections}
        keyExtractor={(item) => item.name}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        stickySectionHeadersEnabled={false}
        renderSectionHeader={({ section }) => (
          <View style={styles.sectionHeader}>
            <Icon name="leaf" size={18} color={Colors.primary} />
            <Text style={styles.sectionTitle}>{section.title}</Text>
            <View style={styles.countBadge}>
              <Text style={styles.sectionCount}>{section.data.length}</Text>
            </View>
          </View>
        )}
        renderItem={({ item }) => (
          <DiseaseListItem name={item.name} disease={item.disease} />
        )}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyText}>No diseases found.</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.sm,
  },
  title: {
    ...Typography.h2,
    color: Colors.textPrimary,
  },
  subtitle: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  filterRow: {
    flexDirection: 'row',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    gap: Spacing.sm,
  },
  filterTab: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm,
    borderRadius: Radius.full,
    backgroundColor: Colors.surfaceMuted,
  },
  filterTabActive: {
    backgroundColor: Colors.surfaceSubtle,
    borderWidth: 1.5,
    borderColor: Colors.primaryLight,
  },
  filterText: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    fontWeight: '500',
  },
  filterTextActive: {
    color: Colors.primary,
    fontWeight: '600',
  },
  listContent: {
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing['3xl'],
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    marginTop: Spacing.lg,
    marginBottom: Spacing.md,
  },
  sectionTitle: {
    ...Typography.h3,
    color: Colors.primaryDark,
    flex: 1,
  },
  countBadge: {
    backgroundColor: Colors.surfaceMuted,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 3,
    borderRadius: Radius.full,
  },
  sectionCount: {
    ...Typography.caption,
    color: Colors.textSecondary,
  },
  empty: {
    paddingVertical: Spacing['4xl'],
    alignItems: 'center',
  },
  emptyText: {
    ...Typography.body,
    color: Colors.textSecondary,
  },
});
