/**
 * Frontend Feature Flags Configuration
 * 
 * This module provides runtime feature flag configuration for the frontend.
 * Feature flags can be controlled via:
 * 1. Environment variables (at build time via .env files)
 * 2. Backend API (at runtime, dynamically fetched)
 * 
 * Priority: Backend API > Environment Variables > Defaults
 */

// Helper to parse boolean from string
const parseBool = (value: string | undefined, defaultValue: boolean = false): boolean => {
  if (value === undefined || value === '') return defaultValue;
  return value.toLowerCase() === 'true' || value === '1';
};

// Environment detection
const getEnvironment = (): string => {
  return import.meta.env.MODE || 'production';
};

const environment = getEnvironment();
const isProduction = environment === 'production';
const isStaging = environment === 'staging';
const isDevelopment = environment === 'development';

// Default for feature flags: OFF in production, ON in staging/dev
const defaultFeatureFlag = isStaging || isDevelopment;

// ============================================================================
// Feature Flags (from environment variables)
// ============================================================================

export interface FeatureFlags {
  ENABLE_CAR_NUMBER: boolean;
  ENABLE_PART_CATEGORIES: boolean;
  ENABLE_TG_ADMIN_NOTIFS: boolean;
  ENABLE_TG_MECH_NOTIFS: boolean;
  ENABLE_MECH_I18N: boolean;
  ENABLE_UI_REFRESH: boolean;
}

// Initial feature flags from environment variables
const envFeatureFlags: FeatureFlags = {
  ENABLE_CAR_NUMBER: parseBool(
    import.meta.env.VITE_ENABLE_CAR_NUMBER,
    defaultFeatureFlag
  ),
  ENABLE_PART_CATEGORIES: parseBool(
    import.meta.env.VITE_ENABLE_PART_CATEGORIES,
    defaultFeatureFlag
  ),
  ENABLE_TG_ADMIN_NOTIFS: parseBool(
    import.meta.env.VITE_ENABLE_TG_ADMIN_NOTIFS,
    defaultFeatureFlag
  ),
  ENABLE_TG_MECH_NOTIFS: parseBool(
    import.meta.env.VITE_ENABLE_TG_MECH_NOTIFS,
    defaultFeatureFlag
  ),
  ENABLE_MECH_I18N: parseBool(
    import.meta.env.VITE_ENABLE_MECH_I18N,
    defaultFeatureFlag
  ),
  ENABLE_UI_REFRESH: parseBool(
    import.meta.env.VITE_ENABLE_UI_REFRESH,
    defaultFeatureFlag
  ),
};

// Runtime feature flags (can be updated from backend)
let runtimeFeatureFlags: FeatureFlags = { ...envFeatureFlags };

// ============================================================================
// Feature Flag API
// ============================================================================

/**
 * Get current feature flags (with runtime overrides if available)
 */
export const getFeatureFlags = (): FeatureFlags => {
  return { ...runtimeFeatureFlags };
};

/**
 * Check if a specific feature is enabled
 */
export const isFeatureEnabled = (feature: keyof FeatureFlags): boolean => {
  return runtimeFeatureFlags[feature];
};

/**
 * Fetch feature flags from backend and update runtime configuration
 * This should be called on app initialization
 */
export const fetchFeatureFlags = async (): Promise<FeatureFlags> => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL || '/api';
    const response = await fetch(`${apiUrl}/config/feature-flags`);
    
    if (!response.ok) {
      console.warn('Failed to fetch feature flags from backend, using environment defaults');
      return runtimeFeatureFlags;
    }
    
    const backendFlags = await response.json();
    
    // Merge backend flags with environment flags (backend takes priority)
    runtimeFeatureFlags = {
      ...envFeatureFlags,
      ...backendFlags,
    };
    
    console.log('Feature flags loaded from backend:', runtimeFeatureFlags);
    return runtimeFeatureFlags;
  } catch (error) {
    console.error('Error fetching feature flags:', error);
    console.warn('Using environment defaults for feature flags');
    return runtimeFeatureFlags;
  }
};

/**
 * Manually set feature flags (useful for testing)
 */
export const setFeatureFlags = (flags: Partial<FeatureFlags>): void => {
  runtimeFeatureFlags = {
    ...runtimeFeatureFlags,
    ...flags,
  };
};

/**
 * Reset feature flags to environment defaults
 */
export const resetFeatureFlags = (): void => {
  runtimeFeatureFlags = { ...envFeatureFlags };
};

// ============================================================================
// Environment Info
// ============================================================================

export const config = {
  environment,
  isProduction,
  isStaging,
  isDevelopment,
  apiUrl: import.meta.env.VITE_API_URL || '/api',
};

// ============================================================================
// Export for convenience
// ============================================================================

export default {
  getFeatureFlags,
  isFeatureEnabled,
  fetchFeatureFlags,
  setFeatureFlags,
  resetFeatureFlags,
  config,
};
