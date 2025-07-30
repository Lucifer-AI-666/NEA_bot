/**
 * Typography System
 * Professional font configuration following modern design principles
 */

import { Platform } from 'react-native';

export const fonts = {
  primary: Platform.select({
    ios: 'System',
    android: 'Roboto',
    default: 'Segoe UI',
  }),
  monospace: Platform.select({
    ios: 'Menlo',
    android: 'monospace',
    default: 'Consolas',
  }),
} as const;

export const typography = {
  // Headings
  h1: {
    fontSize: 28,
    fontWeight: 'bold' as const,
    lineHeight: 36,
    letterSpacing: -0.5,
  },
  h2: {
    fontSize: 24,
    fontWeight: 'bold' as const,
    lineHeight: 32,
    letterSpacing: -0.25,
  },
  h3: {
    fontSize: 20,
    fontWeight: '600' as const,
    lineHeight: 28,
    letterSpacing: 0,
  },
  
  // Body Text
  body: {
    fontSize: 16,
    fontWeight: '400' as const,
    lineHeight: 24,
    letterSpacing: 0,
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: '400' as const,
    lineHeight: 20,
    letterSpacing: 0,
  },
  
  // UI Elements
  button: {
    fontSize: 16,
    fontWeight: '600' as const,
    lineHeight: 20,
    letterSpacing: 0.25,
  },
  caption: {
    fontSize: 12,
    fontWeight: '400' as const,
    lineHeight: 16,
    letterSpacing: 0.4,
  },
  
  // Input
  input: {
    fontSize: 16,
    fontWeight: '400' as const,
    lineHeight: 20,
    letterSpacing: 0,
  },
} as const;

export type Typography = typeof typography;