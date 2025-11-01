# Frontend Configuration

This directory contains frontend configuration modules, including feature flags.

## Files

- **`env.ts`** - Feature flags configuration with runtime API fetching
- **`FeatureFlagsContext.tsx`** - React context provider for feature flags
- **`index.ts`** - Exports for easy importing

## Usage

### 1. Wrap your app with FeatureFlagsProvider

```tsx
// main.tsx
import { FeatureFlagsProvider } from './config';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <FeatureFlagsProvider>
      <App />
    </FeatureFlagsProvider>
  </React.StrictMode>
);
```

### 2. Use feature flags in components

```tsx
import { useFeatureFlags } from '@/config';

function MyComponent() {
  const { isEnabled, flags } = useFeatureFlags();

  return (
    <div>
      {isEnabled('ENABLE_UI_REFRESH') && <NewFeature />}
      {!isEnabled('ENABLE_UI_REFRESH') && <LegacyFeature />}
    </div>
  );
}
```

### 3. Use HOC for conditional rendering

```tsx
import { withFeatureFlag } from '@/config';

const NewFeature = () => <div>New UI</div>;
const OldFeature = () => <div>Old UI</div>;

export default withFeatureFlag('ENABLE_UI_REFRESH', NewFeature, OldFeature);
```

## Available Feature Flags

- `ENABLE_CAR_NUMBER` - Show car number field in forms
- `ENABLE_PART_CATEGORIES` - Use categorized parts catalog
- `ENABLE_TG_ADMIN_NOTIFS` - Admin Telegram notifications
- `ENABLE_TG_MECH_NOTIFS` - Mechanic Telegram notifications
- `ENABLE_MECH_I18N` - Multi-language support
- `ENABLE_UI_REFRESH` - Modernized UI components

## Configuration

Feature flags can be configured via:

1. **Environment variables** (build-time) in `.env` files:
   ```bash
   VITE_ENABLE_UI_REFRESH=true
   ```

2. **Backend API** (runtime) automatically fetched on app load from `/api/config/feature-flags`

Backend API takes priority over environment variables.

## See Also

- `/FEATURE_FLAGS_GUIDE.md` - Complete guide
- `/FEATURE_FLAGS_USAGE_EXAMPLES.md` - Code examples
- `felix_hub/backend/config.py` - Backend configuration
