import React from 'react';
import { ScrollView, View, Text, StyleSheet, StatusBar } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { DiagnosisCard } from '../components/result/DiagnosisCard';
import { TreatmentCard } from '../components/result/TreatmentCard';
import { PreventionList } from '../components/result/PreventionList';
import { ConfidenceBar } from '../components/ui/ConfidenceBar';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import Icon from 'react-native-vector-icons/Ionicons';
import { Colors, Typography, Spacing } from '../theme';
import type { RootStackParamList } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Result'>;

export function ResultScreen({ route, navigation }: Props) {
  const { result, imagePath } = route.params;
  const insets = useSafeAreaInsets();
  const isUrgent = result.treatment.toUpperCase().startsWith('URGENT');

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={Colors.background} />
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={[styles.scrollContent, { paddingBottom: insets.bottom + Spacing['4xl'] }]}
      >
        {/* Main diagnosis */}
        <DiagnosisCard result={result} imagePath={imagePath} />

        {/* Treatment */}
        <View style={styles.section}>
          <TreatmentCard treatment={result.treatment} isUrgent={isUrgent} />
        </View>

        {/* Symptoms */}
        {result.symptoms.length > 0 && (
          <View style={styles.section}>
            <PreventionList
              title="Symptoms"
              items={result.symptoms}
              icon="alert-circle"
              iconColor={Colors.severityModerate}
            />
          </View>
        )}

        {/* Prevention */}
        {result.prevention.length > 0 && (
          <View style={styles.section}>
            <PreventionList title="Prevention" items={result.prevention} />
          </View>
        )}

        {/* Top-K predictions */}
        <View style={styles.section}>
          <Card>
            <View style={styles.topKHeader}>
              <Icon name="bar-chart" size={20} color={Colors.primary} />
              <Text style={styles.topKTitle}>All Predictions</Text>
            </View>
            {result.topK.map((item, index) => (
              <ConfidenceBar
                key={item.className}
                label={item.className}
                confidence={item.confidence}
                isTop={index === 0}
              />
            ))}
          </Card>
        </View>

        {/* Scan again button */}
        <View style={styles.ctaSection}>
          <Button
            title="Scan Another Leaf"
            size="large"
            onPress={() => navigation.goBack()}
            icon={<Icon name="camera" size={22} color={Colors.textOnPrimary} />}
            style={styles.fullWidth}
          />
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  scrollContent: {
    padding: Spacing.lg,
  },
  section: {
    marginTop: Spacing.lg,
  },
  ctaSection: {
    marginTop: Spacing['2xl'],
  },
  fullWidth: {
    width: '100%',
  },
  topKHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    marginBottom: Spacing.lg,
  },
  topKTitle: {
    ...Typography.h3,
    color: Colors.primaryDark,
  },
});
