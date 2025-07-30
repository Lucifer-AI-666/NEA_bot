/**
 * Chat Screen
 * Main chat interface with TAUROS AI bot
 * Professional implementation with TypeScript, proper error handling, and modern styling
 */

import React, { useState, useCallback } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  StyleSheet, 
  ScrollView,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { theme } from '../theme';
import { ChatScreenProps } from '../types/navigation';
import { ROUTES } from '../constants/routes';
import { chatAPI, APIError } from '../utils/api';

interface ChatMessage {
  id: string;
  message: string;
  response: string;
  timestamp: Date;
}

export const ChatScreen: React.FC<ChatScreenProps> = ({ navigation }) => {
  // State Management
  const [message, setMessage] = useState<string>('');
  const [currentResponse, setCurrentResponse] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);

  // Handle message sending with proper error handling
  const handleSend = useCallback(async () => {
    if (!message.trim()) {
      Alert.alert('Attenzione', 'Inserisci un messaggio prima di inviare.');
      return;
    }

    const messageToSend = message.trim();
    setMessage('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(messageToSend);
      const responseText = response.response || 'Risposta non disponibile';
      setCurrentResponse(responseText);

      // Add to chat history
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        message: messageToSend,
        response: responseText,
        timestamp: new Date(),
      };
      setChatHistory(prev => [...prev, newMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      
      let errorMessage = 'Errore nel contatto con TAUROS.';
      if (error instanceof APIError) {
        errorMessage = error.getUserMessage();
      }
      
      setCurrentResponse(errorMessage);
      Alert.alert('Errore', errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [message]);

  // Navigate to settings
  const handleNavigateToSettings = useCallback(() => {
    navigation.navigate(ROUTES.SETTINGS);
  }, [navigation]);

  // Handle input change
  const handleMessageChange = useCallback((text: string) => {
    setMessage(text);
  }, []);

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>TAUROS</Text>
        <Text style={styles.subtitle}>AI Assistant</Text>
      </View>

      {/* Response Display */}
      <ScrollView 
        style={styles.responseContainer}
        contentContainerStyle={styles.responseContent}
        showsVerticalScrollIndicator={false}
      >
        {currentResponse ? (
          <Text style={styles.responseText}>{currentResponse}</Text>
        ) : (
          <Text style={styles.placeholderText}>
            Ciao! Sono TAUROS, il tuo assistente AI. Come posso aiutarti oggi?
          </Text>
        )}
      </ScrollView>

      {/* Input Section */}
      <View style={styles.inputSection}>
        <TextInput
          style={styles.textInput}
          placeholder="Scrivi qui il tuo messaggio..."
          placeholderTextColor={theme.colors.input.placeholder}
          value={message}
          onChangeText={handleMessageChange}
          multiline
          maxLength={1000}
          editable={!isLoading}
        />
        
        {/* Action Buttons */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.button, styles.primaryButton, isLoading && styles.disabledButton]}
            onPress={handleSend}
            disabled={isLoading}
          >
            <Text style={styles.primaryButtonText}>
              {isLoading ? 'Invio...' : 'Invia'}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.button, styles.secondaryButton]}
            onPress={handleNavigateToSettings}
          >
            <Text style={styles.secondaryButtonText}>Impostazioni</Text>
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.primary.background,
  },
  header: {
    paddingTop: theme.spacing.xl,
    paddingHorizontal: theme.spacing.lg,
    paddingBottom: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.primary.border,
  },
  title: {
    ...theme.typography.h1,
    color: theme.colors.primary.accent,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  subtitle: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    marginTop: theme.spacing.xs,
  },
  responseContainer: {
    flex: 1,
    paddingHorizontal: theme.spacing.lg,
  },
  responseContent: {
    paddingVertical: theme.spacing.lg,
    minHeight: '100%',
  },
  responseText: {
    ...theme.typography.body,
    color: theme.colors.text.primary,
    lineHeight: 24,
  },
  placeholderText: {
    ...theme.typography.body,
    color: theme.colors.text.muted,
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: theme.spacing.xxl,
  },
  inputSection: {
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
    borderTopWidth: 1,
    borderTopColor: theme.colors.primary.border,
    backgroundColor: theme.colors.primary.surface,
  },
  textInput: {
    ...theme.typography.input,
    backgroundColor: theme.colors.input.background,
    color: theme.colors.text.primary,
    borderWidth: 1,
    borderColor: theme.colors.input.border,
    borderRadius: theme.borderRadius.md,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    minHeight: theme.layout.inputHeight,
    maxHeight: 120,
    textAlignVertical: 'top',
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: theme.spacing.sm,
    marginTop: theme.spacing.md,
  },
  button: {
    flex: 1,
    height: theme.layout.buttonHeight,
    borderRadius: theme.borderRadius.md,
    justifyContent: 'center',
    alignItems: 'center',
  },
  primaryButton: {
    backgroundColor: theme.colors.button.primary,
  },
  primaryButtonText: {
    ...theme.typography.button,
    color: theme.colors.text.inverse,
  },
  secondaryButton: {
    backgroundColor: theme.colors.button.secondary,
    borderWidth: 1,
    borderColor: theme.colors.primary.border,
  },
  secondaryButtonText: {
    ...theme.typography.button,
    color: theme.colors.text.primary,
  },
  disabledButton: {
    opacity: 0.6,
  },
});