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
        {/* Hero */}
        <HeroSection />

        {/* Features */}
        <View style={styles.features}>
          <FeatureCard
            icon="camera"
            title="Instant Scan"
            description="Take a photo of any leaf and get disease diagnosis in under a second."
            color={Colors.primary}
          />
          <FeatureCard
            icon="cloud-offline"
            title="Works Offline"
            description="AI model runs entirely on your device. No internet needed."
            color="#1976D2"
          />
          <FeatureCard
            icon="library"
            title="Disease Library"
            description="Browse all 15 supported diseases with symptoms, treatment, and prevention."
            color="#7B1FA2"
          />
        </View>

        {/* CTA Button */}
        <View style={styles.ctaContainer}>
          <Button
            title="Scan a Leaf"
            onPress={() => navigation.navigate('MainTabs', { screen: 'Scan' })}
            icon={<Icon name="scan" size={20} color={Colors.textOnPrimary} />}
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
    paddingBottom: Spacing['4xl'],
  },
  features: {
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing['2xl'],
  },
  ctaContainer: {
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.lg,
  },
  ctaButton: {
    width: '100%',
  },
});
