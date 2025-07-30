/**
 * Spacing & Layout System
 * Consistent spacing using 8px grid system
 */

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
} as const;

export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  round: 50,
} as const;

export const layout = {
  screenPadding: spacing.lg,
  cardPadding: spacing.md,
  buttonHeight: 44,
  inputHeight: 44,
  headerHeight: 60,
} as const;

export type Spacing = typeof spacing;
export type BorderRadius = typeof borderRadius;
export type Layout = typeof layout;