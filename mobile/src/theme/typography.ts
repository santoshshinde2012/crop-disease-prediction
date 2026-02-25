import { TextStyle, Platform } from 'react-native';

const fontFamily = Platform.select({
  ios: 'System',
  android: 'Roboto',
  default: 'System',
});

export const Typography = {
  /** 28px bold — screen titles, hero heading */
  h1: {
    fontFamily,
    fontSize: 28,
    fontWeight: '700',
    lineHeight: 34,
  } as TextStyle,

  /** 22px semibold — section headings */
  h2: {
    fontFamily,
    fontSize: 22,
    fontWeight: '600',
    lineHeight: 28,
  } as TextStyle,

  /** 18px semibold — card titles */
  h3: {
    fontFamily,
    fontSize: 18,
    fontWeight: '600',
    lineHeight: 24,
  } as TextStyle,

  /** 16px regular — body text */
  body: {
    fontFamily,
    fontSize: 16,
    fontWeight: '400',
    lineHeight: 22,
  } as TextStyle,

  /** 14px regular — secondary text */
  bodySmall: {
    fontFamily,
    fontSize: 14,
    fontWeight: '400',
    lineHeight: 20,
  } as TextStyle,

  /** 12px medium — labels, badges */
  caption: {
    fontFamily,
    fontSize: 12,
    fontWeight: '500',
    lineHeight: 16,
  } as TextStyle,

  /** 16px semibold — buttons */
  button: {
    fontFamily,
    fontSize: 16,
    fontWeight: '600',
    lineHeight: 22,
  } as TextStyle,

  /** 36px bold — large numbers (confidence %) */
  display: {
    fontFamily,
    fontSize: 36,
    fontWeight: '700',
    lineHeight: 42,
  } as TextStyle,
} as const;
