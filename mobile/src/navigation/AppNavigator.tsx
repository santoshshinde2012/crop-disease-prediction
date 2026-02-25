import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/Ionicons';
import { HomeScreen } from '../screens/HomeScreen';
import { CameraScreen } from '../screens/CameraScreen';
import { ResultScreen } from '../screens/ResultScreen';
import { HistoryScreen } from '../screens/HistoryScreen';
import { DiseaseLibraryScreen } from '../screens/DiseaseLibraryScreen';
import { Colors, Typography } from '../theme';
import type { RootStackParamList, TabParamList } from '../types';

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<TabParamList>();

const TAB_ICONS: Record<keyof TabParamList, { active: string; inactive: string }> = {
  Home: { active: 'home', inactive: 'home-outline' },
  Scan: { active: 'scan-circle', inactive: 'scan-circle-outline' },
  History: { active: 'time', inactive: 'time-outline' },
  Library: { active: 'library', inactive: 'library-outline' },
};

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, size }) => {
          const icons = TAB_ICONS[route.name];
          return (
            <Icon
              name={focused ? icons.active : icons.inactive}
              size={size}
              color={focused ? Colors.primary : Colors.textSecondary}
            />
          );
        },
        tabBarActiveTintColor: Colors.primary,
        tabBarInactiveTintColor: Colors.textSecondary,
        tabBarLabelStyle: {
          ...Typography.caption,
          fontSize: 11,
        },
        tabBarStyle: {
          backgroundColor: Colors.surface,
          borderTopColor: Colors.border,
          height: 60,
          paddingBottom: 8,
          paddingTop: 4,
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen
        name="Scan"
        component={CameraScreen}
        options={{ tabBarLabel: 'Scan' }}
      />
      <Tab.Screen name="History" component={HistoryScreen} />
      <Tab.Screen
        name="Library"
        component={DiseaseLibraryScreen}
        options={{ tabBarLabel: 'Library' }}
      />
    </Tab.Navigator>
  );
}

export function AppNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="MainTabs" component={MainTabs} />
      <Stack.Screen
        name="Result"
        component={ResultScreen}
        options={{
          headerShown: true,
          title: 'Diagnosis Result',
          headerTintColor: Colors.primaryDark,
          headerStyle: { backgroundColor: Colors.background },
          headerTitleStyle: { ...Typography.h3, color: Colors.textPrimary },
        }}
      />
    </Stack.Navigator>
  );
}
