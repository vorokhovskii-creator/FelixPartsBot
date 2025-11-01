/**
 * Feature Flags React Context
 * 
 * Provides feature flags to all components via React Context.
 * Automatically fetches feature flags from backend on mount.
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { getFeatureFlags, fetchFeatureFlags, isFeatureEnabled, FeatureFlags } from './env';

interface FeatureFlagsContextType {
  flags: FeatureFlags;
  isLoading: boolean;
  isEnabled: (feature: keyof FeatureFlags) => boolean;
  refresh: () => Promise<void>;
}

const FeatureFlagsContext = createContext<FeatureFlagsContextType | undefined>(undefined);

interface FeatureFlagsProviderProps {
  children: ReactNode;
}

export const FeatureFlagsProvider: React.FC<FeatureFlagsProviderProps> = ({ children }) => {
  const [flags, setFlags] = useState<FeatureFlags>(getFeatureFlags());
  const [isLoading, setIsLoading] = useState(true);

  const loadFeatureFlags = async () => {
    setIsLoading(true);
    try {
      const updatedFlags = await fetchFeatureFlags();
      setFlags(updatedFlags);
    } catch (error) {
      console.error('Failed to load feature flags:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadFeatureFlags();
  }, []);

  const contextValue: FeatureFlagsContextType = {
    flags,
    isLoading,
    isEnabled: (feature: keyof FeatureFlags) => isFeatureEnabled(feature),
    refresh: loadFeatureFlags,
  };

  return (
    <FeatureFlagsContext.Provider value={contextValue}>
      {children}
    </FeatureFlagsContext.Provider>
  );
};

/**
 * Hook to access feature flags
 * 
 * @example
 * const { flags, isEnabled } = useFeatureFlags();
 * 
 * if (isEnabled('ENABLE_UI_REFRESH')) {
 *   // Render new UI
 * }
 */
export const useFeatureFlags = (): FeatureFlagsContextType => {
  const context = useContext(FeatureFlagsContext);
  
  if (!context) {
    throw new Error('useFeatureFlags must be used within a FeatureFlagsProvider');
  }
  
  return context;
};

/**
 * HOC to conditionally render components based on feature flags
 * 
 * @example
 * const NewFeature = withFeatureFlag('ENABLE_UI_REFRESH', () => <div>New UI</div>);
 */
export function withFeatureFlag<P extends object>(
  feature: keyof FeatureFlags,
  Component: React.ComponentType<P>,
  Fallback?: React.ComponentType<P>
): React.FC<P> {
  return (props: P) => {
    const { isEnabled } = useFeatureFlags();
    
    if (isEnabled(feature)) {
      return <Component {...props} />;
    }
    
    return Fallback ? <Fallback {...props} /> : null;
  };
}
