import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { InferenceModeProvider } from './src/context/InferenceModeContext';
import { ModelProvider } from './src/context/ModelContext';
import { AppNavigator } from './src/navigation/AppNavigator';
import { Colors } from './src/theme';

export default function App() {
  return (
    <SafeAreaProvider>
      <InferenceModeProvider>
        <ModelProvider>
          <NavigationContainer
            theme={{
              dark: false,
              colors: {
                primary: Colors.primary,
                background: Colors.background,
                card: Colors.surface,
                text: Colors.textPrimary,
                border: Colors.border,
                notification: Colors.severityHigh,
              },
            }}
          >
            <AppNavigator />
          </NavigationContainer>
        </ModelProvider>
      </InferenceModeProvider>
    </SafeAreaProvider>
  );
}
