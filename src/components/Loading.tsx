/**
 * Loading Component
 * Custom fallback for React.Suspense with professional styling
 */

import React from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { theme } from '../theme';

interface LoadingProps {
  message?: string;
  size?: 'small' | 'large';
}

export const Loading: React.FC<LoadingProps> = ({ 
  message = 'Caricamento...', 
  size = 'large' 
}) => {
  return (
    <View style={styles.container}>
      <ActivityIndicator 
        size={size} 
        color={theme.colors.primary.accent} 
      />
      <Text style={styles.message}>{message}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.primary.background,
    padding: theme.spacing.lg,
  },
  message: {
    ...theme.typography.body,
    color: theme.colors.text.secondary,
    marginTop: theme.spacing.md,
    textAlign: 'center',
  },
});