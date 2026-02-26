import React from 'react';
import { ScrollView, View, StyleSheet, StatusBar } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { HeroSection } from '../components/home/HeroSection';
import { FeatureCard } from '../components/home/FeatureCard';
import { Button } from '../components/ui/Button';
import Icon from 'react-native-vector-icons/Ionicons';
import { Colors, Spacing } from '../theme';
import type { RootStackParamList } from '../types';

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

export function HomeScreen() {
  const navigation = useNavigation<NavigationProp>();

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primaryDark} />
      <ScrollView
        bounces={false}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {/* Hero (includes mode toggle) */}
        <HeroSection />

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
            description="Browse 15 supported diseases with clear guidance."
            color="#7B1FA2"
          />
        </View>
      </ScrollView>

      {/* Fixed CTA — always visible */}
      <View style={styles.footer}>
        <Button
          title="Scan a Leaf"
          size="large"
          onPress={() => navigation.navigate('MainTabs', { screen: 'Scan' })}
          icon={<Icon name="scan" size={22} color={Colors.textOnPrimary} />}
          style={styles.ctaButton}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  scrollContent: {
    paddingBottom: Spacing.lg,
  },
  features: {
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.lg,
  },
  footer: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    backgroundColor: Colors.background,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: Colors.borderLight,
  },
  ctaButton: {
    width: '100%',
  },
});
