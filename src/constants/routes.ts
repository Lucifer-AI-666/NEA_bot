/**
 * Navigation Routes
 * Centralized route constants for type safety and maintainability
 */

export const ROUTES = {
  CHAT: 'Chat',
  SETTINGS: 'Settings',
} as const;

export type Route = typeof ROUTES[keyof typeof ROUTES];

// Screen Configuration
export const SCREEN_OPTIONS = {
  headerShown: false,
  gestureEnabled: true,
  animationTypeForReplace: 'push',
} as const;