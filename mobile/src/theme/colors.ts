/** Color palette — consistent with Streamlit app (streamlit_app/styles.py) */
export const Colors = {
  // Primary greens
  primary: '#2E7D32',
  primaryLight: '#4CAF50',
  primaryDark: '#1B5E20',
  accent: '#81C784',

  // Backgrounds
  background: '#FAFAFA',
  surface: '#FFFFFF',
  surfaceSubtle: '#F1F8E9',
  surfaceMuted: '#F5F5F5',

  // Text
  textPrimary: '#1B1B1B',
  textSecondary: '#5F6368',
  textOnPrimary: '#FFFFFF',
  textOnDark: '#FFFFFF',

  // Severity
  severityHigh: '#D32F2F',
  severityModerate: '#F57C00',
  severityNone: '#2E7D32',

  severityHighBg: '#FFEBEE',
  severityModerateBg: '#FFF3E0',
  severityNoneBg: '#E8F5E9',

  // Utility
  border: '#E0E0E0',
  borderLight: '#C8E6C9',
  shadow: '#000000',
  overlay: 'rgba(0, 0, 0, 0.5)',
  transparent: 'transparent',

  // Confidence bar
  barTrack: '#E8F5E9',
  barFillHigh: '#2E7D32',
  barFillMedium: '#F57C00',
  barFillLow: '#D32F2F',
} as const;

/** Gradient presets */
export const Gradients = {
  primary: ['#1B5E20', '#2E7D32', '#4CAF50'] as const,
  hero: ['#1B5E20', '#2E7D32'] as const,
  card: ['#FFFFFF', '#F1F8E9'] as const,
} as const;
