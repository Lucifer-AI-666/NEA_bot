
/**
 * App.tsx - Main Application Entry Point
 * Professional React Native implementation with TypeScript best practices
 * 
 * Features:
 * - Lazy loading of components for optimal performance
 * - Type-safe navigation with TypeScript
 * - Professional error handling with ErrorBoundary
 * - Consistent dark theme (#0d1117 background, #c9d1d9 text)
 * - Modular architecture for easy scalability
 * - Custom Suspense fallback component
 * - Centralized route constants
 */

import React, { Suspense, lazy } from 'react';
import { StatusBar } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

// Theme and Constants
import { theme } from './src/theme';
import { ROUTES, SCREEN_OPTIONS } from './src/constants/routes';

// Types
import type { RootStackParamList } from './src/types/navigation';

// Components
import { Loading } from './src/components/Loading';
import { ErrorBoundary } from './src/components/ErrorBoundary';

// Lazy-loaded screens for optimal performance
const ChatScreen = lazy(() => 
  import('./src/screens/ChatScreen').then(module => ({ 
    default: module.ChatScreen 
  }))
);

const SettingsScreen = lazy(() => 
  import('./src/screens/SettingsScreen').then(module => ({ 
    default: module.SettingsScreen 
  }))
);

// Stack Navigator
const Stack = createNativeStackNavigator<RootStackParamList>();

// Custom loading fallback component
const LoadingFallback: React.FC = () => (
  <Loading message="Caricamento schermata..." size="large" />
);

// Navigation theme configuration
const navigationTheme = {
  dark: true,
  colors: {
    primary: theme.colors.primary.accent,
    background: theme.colors.primary.background,
    card: theme.colors.primary.surface,
    text: theme.colors.text.primary,
    border: theme.colors.primary.border,
    notification: theme.colors.status.info,
  },
};

/**
 * Main App Component
 * Implements professional architecture with error boundaries,
 * lazy loading, and consistent theming
 */
const App: React.FC = () => {
  return (
    <ErrorBoundary fallbackMessage="Errore nell'inizializzazione dell'app">
      {/* Status Bar Configuration */}
      <StatusBar 
        barStyle="light-content" 
        backgroundColor={theme.colors.primary.background}
        translucent={false}
      />
      
      {/* Navigation Container */}
      <NavigationContainer theme={navigationTheme}>
        <Stack.Navigator
          initialRouteName={ROUTES.CHAT}
          screenOptions={SCREEN_OPTIONS}
        >
          {/* Chat Screen - Main Entry Point */}
          <Stack.Screen 
            name={ROUTES.CHAT}
            options={{
              title: 'TAUROS Chat',
              headerShown: false,
            }}
          >
            {(props) => (
              <ErrorBoundary fallbackMessage="Errore nel caricamento della chat">
                <Suspense fallback={<LoadingFallback />}>
                  <ChatScreen {...props} />
                </Suspense>
              </ErrorBoundary>
            )}
          </Stack.Screen>

          {/* Settings Screen */}
          <Stack.Screen 
            name={ROUTES.SETTINGS}
            options={{
              title: 'Impostazioni',
              headerShown: false,
            }}
          >
            {(props) => (
              <ErrorBoundary fallbackMessage="Errore nel caricamento delle impostazioni">
                <Suspense fallback={<LoadingFallback />}>
                  <SettingsScreen {...props} />
                </Suspense>
              </ErrorBoundary>
            )}
          </Stack.Screen>
        </Stack.Navigator>
      </NavigationContainer>
    </ErrorBoundary>
  );
};

export default App;

/**
 * Export types for external usage
 */
export type { RootStackParamList } from './src/types/navigation';
