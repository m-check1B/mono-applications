/**
 * i18next Configuration
 * 
 * Simple internationalization without Next.js complexity.
 * Works with any React app!
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Import translations
import enTranslations from './locales/en.json';
import csTranslations from './locales/cs.json';
import deTranslations from './locales/de.json';

export const defaultNS = 'common';
export const resources = {
  en: {
    common: enTranslations.common,
    auth: enTranslations.auth,
    tasks: enTranslations.tasks,
    calls: enTranslations.calls,
  },
  cs: {
    common: csTranslations.common,
    auth: csTranslations.auth,
    tasks: csTranslations.tasks,
    calls: csTranslations.calls,
  },
  de: {
    common: deTranslations.common,
    auth: deTranslations.auth,
    tasks: deTranslations.tasks,
    calls: deTranslations.calls,
  },
} as const;

i18n
  .use(Backend) // Load translations from files
  .use(LanguageDetector) // Detect user language
  .use(initReactI18next) // Pass i18n instance to react-i18next
  .init({
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    defaultNS,
    ns: ['common', 'auth', 'tasks', 'calls'],
    
    // Use bundled resources for now
    resources,
    
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    
    detection: {
      order: ['localStorage', 'cookie', 'navigator', 'htmlTag'],
      caches: ['localStorage', 'cookie'],
    },
    
    react: {
      useSuspense: false, // Disable suspense for SSR compatibility
    },
  });

export default i18n;

// Type-safe translation hook
import { useTranslation as useTranslationBase } from 'react-i18next';

export function useTranslation(ns?: keyof typeof resources['en']) {
  return useTranslationBase(ns);
}