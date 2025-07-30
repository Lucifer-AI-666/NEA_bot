/**
 * Design System - Color Palette
 * Professional dark theme configuration following GitHub Dark theme
 */

export const colors = {
  // Primary Dark Theme Colors
  primary: {
    background: '#0d1117', // Main background - GitHub dark
    surface: '#161b22',    // Card/surface background
    border: '#30363d',     // Border color
    accent: '#33cc99',     // Accent color (keeping original teal)
  },
  
  // Text Colors
  text: {
    primary: '#c9d1d9',    // Primary text - GitHub dark
    secondary: '#8b949e',  // Secondary text
    muted: '#6e7681',      // Muted text
    inverse: '#0d1117',    // Inverse text (for buttons)
  },
  
  // Input Colors
  input: {
    background: '#21262d',
    border: '#30363d',
    focus: '#58a6ff',
    placeholder: '#6e7681',
  },
  
  // Status Colors
  status: {
    success: '#238636',
    warning: '#d29922',
    error: '#da3633',
    info: '#1f6feb',
  },
  
  // Component Colors
  button: {
    primary: '#238636',
    primaryHover: '#2ea043',
    secondary: '#21262d',
    secondaryHover: '#30363d',
  },
} as const;

export type Colors = typeof colors;