/**
 * Navigation Types
 * Type-safe navigation parameters and screens
 */

import { NativeStackScreenProps } from '@react-navigation/native-stack';

// Root Stack Parameter List
export type RootStackParamList = {
  Chat: undefined;
  Settings: undefined;
};

// Screen Props Types
export type ChatScreenProps = NativeStackScreenProps<RootStackParamList, 'Chat'>;
export type SettingsScreenProps = NativeStackScreenProps<RootStackParamList, 'Settings'>;

// Navigation Prop Types
export type RootStackNavigationProp = ChatScreenProps['navigation'];

// Generic Screen Props
export type ScreenProps<T extends keyof RootStackParamList> = NativeStackScreenProps<
  RootStackParamList,
  T
>;