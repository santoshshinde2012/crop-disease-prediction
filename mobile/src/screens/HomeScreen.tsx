import React from 'react';
import { ScrollView, View, StyleSheet, StatusBar } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { HeroSection } from '../components/home/HeroSection';
import { FeatureCard } from '../components/home/FeatureCard';
import { Button } from '../components/ui/Button';
import { ModeToggle } from '../components/ui/ModeToggle';
import Icon from 'react-native-vector-icons/Ionicons';
import { Colors, Spacing } from '../theme';
import type { RootStackParamList } from '../types';

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

export function HomeScreen() {
  const navigation = useNavigation<NavigationProp>();
  const insets = useSafeAreaInsets();

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primaryDark} />
      <ScrollView
        bounces={false}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={[styles.scrollContent, { paddingBottom: insets.bottom + Spacing['5xl'] }]}
      >
        {/* Hero */}
        <HeroSection />

        {/* Inference mode toggle */}
        <View style={styles.toggleContainer}>
          <ModeToggle />
        </View>

        {/* Features */}
        <View style={styles.features}>
          <FeatureCard
            icon="camera"
            title="Instant Scan"
            description="Diagnose crop diseases in seconds from a single leaf photo."
            color={Colors.primary}
          />
          <FeatureCard
            icon="cloud-offline"
            title="Works Offline"
            description="All AI runs entirely on your device. No connection required."
            color="#1976D2"
          />
          <FeatureCard
            icon="library"
            title="Disease Library"
            description="Browse 15 supported diseases with clear guidance and recommendations."
            color="#7B1FA2"
          />
        </View>

        {/* CTA Button */}
        <View style={styles.ctaContainer}>
          <Button
            title="Scan a Leaf"
            size="large"
            onPress={() => navigation.navigate('MainTabs', { screen: 'Scan' })}
            icon={<Icon name="scan" size={22} color={Colors.textOnPrimary} />}
            style={styles.ctaButton}
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
    // paddingBottom set dynamically for safe area
  },
  toggleContainer: {
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.xl,
    alignItems: 'center',
  },
  features: {
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.xl,
  },
  ctaContainer: {
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.sm,
  },
  ctaButton: {
    width: '100%',
  },
});
