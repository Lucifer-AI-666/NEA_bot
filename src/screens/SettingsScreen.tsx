/**
 * Settings Screen
 * Application settings and configuration
 * Professional implementation with TypeScript and modern styling
 */

import React, { useState, useCallback } from 'react';
import { 
  View, 
  Text, 
  Switch, 
  TouchableOpacity, 
  StyleSheet, 
  ScrollView,
  Alert,
} from 'react-native';
import { theme } from '../theme';
import { SettingsScreenProps } from '../types/navigation';

interface SettingItem {
  id: string;
  title: string;
  description?: string;
  type: 'switch' | 'button' | 'info';
  value?: boolean;
  onPress?: () => void;
  onValueChange?: (value: boolean) => void;
}

export const SettingsScreen: React.FC<SettingsScreenProps> = ({ navigation }) => {
  // State Management
  const [gptMode, setGptMode] = useState<boolean>(true);
  const [notifications, setNotifications] = useState<boolean>(true);
  const [darkMode, setDarkMode] = useState<boolean>(true);

  // Handlers
  const handleGptModeToggle = useCallback((value: boolean) => {
    setGptMode(value);
    // Here you would typically save to AsyncStorage or context
  }, []);

  const handleNotificationsToggle = useCallback((value: boolean) => {
    setNotifications(value);
  }, []);

  const handleDarkModeToggle = useCallback((value: boolean) => {
    setDarkMode(value);
    Alert.alert(
      'Modalità Tema', 
      'La modalità tema verrà applicata al prossimo riavvio dell\'app.'
    );
  }, []);

  const handleAboutPress = useCallback(() => {
    Alert.alert(
      'TAUROS v1.0.0',
      'Assistente AI sviluppato per fornire supporto intelligente e conversazioni naturali.\n\nSviluppato con React Native & TypeScript.',
      [{ text: 'OK' }]
    );
  }, []);

  const handleBackPress = useCallback(() => {
    navigation.goBack();
  }, [navigation]);

  // Settings configuration
  const settingsData: SettingItem[] = [
    {
      id: 'gpt-mode',
      title: 'Modalità GPT',
      description: 'Abilita le funzionalità avanzate di intelligenza artificiale',
      type: 'switch',
      value: gptMode,
      onValueChange: handleGptModeToggle,
    },
    {
      id: 'notifications',
      title: 'Notifiche',
      description: 'Ricevi notifiche per nuovi messaggi e aggiornamenti',
      type: 'switch',
      value: notifications,
      onValueChange: handleNotificationsToggle,
    },
    {
      id: 'dark-mode',
      title: 'Tema Scuro',
      description: 'Utilizza il tema scuro per una migliore esperienza visiva',
      type: 'switch',
      value: darkMode,
      onValueChange: handleDarkModeToggle,
    },
    {
      id: 'about',
      title: 'Informazioni',
      description: 'Versione app e dettagli sviluppatore',
      type: 'button',
      onPress: handleAboutPress,
    },
  ];

  const renderSettingItem = (item: SettingItem) => {
    switch (item.type) {
      case 'switch':
        return (
          <View key={item.id} style={styles.settingItem}>
            <View style={styles.settingTextContainer}>
              <Text style={styles.settingTitle}>{item.title}</Text>
              {item.description && (
                <Text style={styles.settingDescription}>{item.description}</Text>
              )}
            </View>
            <Switch
              value={item.value}
              onValueChange={item.onValueChange}
              trackColor={{
                false: theme.colors.input.border,
                true: theme.colors.primary.accent,
              }}
              thumbColor={
                item.value 
                  ? theme.colors.text.primary 
                  : theme.colors.text.secondary
              }
            />
          </View>
        );

      case 'button':
        return (
          <TouchableOpacity
            key={item.id}
            style={styles.settingItem}
            onPress={item.onPress}
          >
            <View style={styles.settingTextContainer}>
              <Text style={styles.settingTitle}>{item.title}</Text>
              {item.description && (
                <Text style={styles.settingDescription}>{item.description}</Text>
              )}
            </View>
            <Text style={styles.chevron}>›</Text>
          </TouchableOpacity>
        );

      default:
        return null;
    }
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={handleBackPress}>
          <Text style={styles.backButtonText}>‹ Indietro</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Impostazioni</Text>
        <View style={styles.headerSpacer} />
      </View>

      {/* Settings List */}
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Preferenze</Text>
          {settingsData.map(renderSettingItem)}
        </View>

        {/* App Info */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            TAUROS AI Assistant
          </Text>
          <Text style={styles.footerSubtext}>
            Versione 1.0.0 • React Native
          </Text>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.primary.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: theme.spacing.xl,
    paddingHorizontal: theme.spacing.lg,
    paddingBottom: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.primary.border,
  },
  backButton: {
    paddingVertical: theme.spacing.xs,
  },
  backButtonText: {
    ...theme.typography.body,
    color: theme.colors.primary.accent,
    fontSize: 18,
  },
  title: {
    ...theme.typography.h2,
    color: theme.colors.text.primary,
    flex: 1,
    textAlign: 'center',
  },
  headerSpacer: {
    width: 60, // Balance the back button
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: theme.spacing.xl,
  },
  section: {
    paddingHorizontal: theme.spacing.lg,
    paddingTop: theme.spacing.lg,
  },
  sectionTitle: {
    ...theme.typography.h3,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing.md,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.primary.border,
  },
  settingTextContainer: {
    flex: 1,
    marginRight: theme.spacing.md,
  },
  settingTitle: {
    ...theme.typography.body,
    color: theme.colors.text.primary,
    fontWeight: '500',
  },
  settingDescription: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
    marginTop: theme.spacing.xs,
  },
  chevron: {
    ...theme.typography.h2,
    color: theme.colors.text.muted,
    fontWeight: '300',
  },
  footer: {
    alignItems: 'center',
    paddingHorizontal: theme.spacing.lg,
    paddingTop: theme.spacing.xxl,
  },
  footerText: {
    ...theme.typography.body,
    color: theme.colors.text.secondary,
    fontWeight: '600',
  },
  footerSubtext: {
    ...theme.typography.caption,
    color: theme.colors.text.muted,
    marginTop: theme.spacing.xs,
  },
});