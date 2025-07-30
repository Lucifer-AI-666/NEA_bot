/**
 * Theme Configuration
 * Centralized theme system for consistent styling across the app
 */

import { colors } from './colors';
import { typography, fonts } from './typography';
import { spacing, borderRadius, layout } from './layout';

export const theme = {
  colors,
  typography,
  fonts,
  spacing,
  borderRadius,
  layout,
} as const;

export type Theme = typeof theme;

// Re-export all theme parts for convenient imports
export { colors, typography, fonts, spacing, borderRadius, layout };
export type { Colors } from './colors';
export type { Typography } from './typography';
export type { Spacing, BorderRadius, Layout } from './layout';