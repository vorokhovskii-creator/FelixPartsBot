# Feature Flags & Safe Rollout Guide

This guide explains how to use feature flags in Felix Hub for safe rollout of new features.

## Overview

Feature flags allow you to:
- Enable/disable features without redeploying code
- Test features in staging before production
- Gradually roll out features to users
- Quickly disable problematic features

## Available Feature Flags

### 1. ENABLE_CAR_NUMBER
**Purpose**: Enables the car number field in order forms  
**Default**: ON in staging/development, OFF in production  
**Scope**: Backend validation, Frontend UI  

### 2. ENABLE_PART_CATEGORIES
**Purpose**: Enables categorized parts catalog view  
**Default**: ON in staging/development, OFF in production  
**Scope**: Backend API, Frontend catalog UI  

### 3. ENABLE_TG_ADMIN_NOTIFS
**Purpose**: Sends Telegram notifications to admins for new orders  
**Default**: ON in staging/development, OFF in production  
**Scope**: Backend notification system  

### 4. ENABLE_TG_MECH_NOTIFS
**Purpose**: Sends Telegram notifications to mechanics for status changes  
**Default**: ON in staging/development, OFF in production  
**Scope**: Backend notification system  

### 5. ENABLE_MECH_I18N
**Purpose**: Enables multi-language support in mechanic interface  
**Default**: ON in staging/development, OFF in production  
**Scope**: Frontend i18n system  

### 6. ENABLE_UI_REFRESH
**Purpose**: Enables modernized UI components and styling  
**Default**: ON in staging/development, OFF in production  
**Scope**: Frontend components  

## Configuration

### Backend Configuration

Feature flags are centralized in `felix_hub/backend/config.py`. They read from environment variables with intelligent defaults based on the environment.

```python
import config

# Use feature flags in your code
if config.ENABLE_CAR_NUMBER:
    # Feature is enabled
    ...
```

### Frontend Configuration

Feature flags are managed in `felix_hub/frontend/src/config/env.ts`. They can be:
1. Set at build time via environment variables
2. Fetched dynamically from the backend API at runtime

```typescript
import { isFeatureEnabled, fetchFeatureFlags } from '@/config/env';

// Fetch feature flags on app startup
await fetchFeatureFlags();

// Check if a feature is enabled
if (isFeatureEnabled('ENABLE_UI_REFRESH')) {
  // Feature is enabled
  ...
}
```

## Environment Variables

### Setting Environment Variables

Create or update `.env` file in the project root:

```bash
# Set environment type
ENVIRONMENT=staging  # Options: production, staging, development

# Override individual flags
ENABLE_CAR_NUMBER=true
ENABLE_PART_CATEGORIES=true
ENABLE_TG_ADMIN_NOTIFS=false  # Disable notifications
ENABLE_TG_MECH_NOTIFS=false
ENABLE_MECH_I18N=true
ENABLE_UI_REFRESH=true
```

### Frontend Environment Variables

For frontend-only overrides, create `.env.local` in `felix_hub/frontend/`:

```bash
VITE_API_URL=http://localhost:5000/api
VITE_ENABLE_UI_REFRESH=true
VITE_ENABLE_MECH_I18N=true
```

## Environment-Based Defaults

Feature flags have intelligent defaults based on the environment:

| Environment | Default Value |
|-------------|---------------|
| `production` | `false` (OFF) |
| `staging` | `true` (ON) |
| `development` | `true` (ON) |
| `testing` | `true` (ON) |

This ensures production remains stable by default while new features are tested in non-production environments.

## Safe Rollout Process

### 1. Development & Testing

```bash
# Set environment to development
ENVIRONMENT=development

# All feature flags default to ON
# Test new features locally
```

### 2. Staging Deployment

```bash
# Set environment to staging
ENVIRONMENT=staging

# All feature flags default to ON
# Test in staging environment
```

### 3. Production Rollout (Gradual)

```bash
# Set environment to production
ENVIRONMENT=production

# Explicitly enable only tested features
ENABLE_CAR_NUMBER=true
ENABLE_PART_CATEGORIES=false  # Keep OFF until ready

# Other flags remain OFF by default
```

### 4. Monitoring

After enabling a feature in production:
1. Monitor application logs for errors
2. Check notification system logs
3. Gather user feedback
4. Use feature flag to quickly disable if issues arise

### 5. Emergency Rollback

If a feature causes issues in production:

```bash
# Quickly disable the problematic feature
ENABLE_PROBLEMATIC_FEATURE=false

# Restart backend (no code changes needed)
# Frontend will fetch updated flags on next reload
```

## Runtime Configuration (Backend Only)

Backend feature flags can be changed at runtime by:

1. Updating environment variables
2. Restarting the backend service

No code redeployment is required.

## Build-Time Configuration (Frontend)

Frontend feature flags are compiled into the build. To change them:

1. Update `.env.production` or environment variables
2. Rebuild the frontend
3. Redeploy the static assets

**Note**: Frontend can also fetch flags from backend API at runtime for dynamic updates.

## API Endpoint

Feature flags are exposed via API for frontend consumption:

```
GET /api/config/feature-flags
```

Response:
```json
{
  "ENABLE_CAR_NUMBER": true,
  "ENABLE_PART_CATEGORIES": true,
  "ENABLE_TG_ADMIN_NOTIFS": false,
  "ENABLE_TG_MECH_NOTIFS": false,
  "ENABLE_MECH_I18N": true,
  "ENABLE_UI_REFRESH": true
}
```

## Best Practices

1. **Start Conservative**: New features should default to OFF in production
2. **Test Thoroughly**: Always test in staging before production
3. **Monitor Closely**: Watch logs and metrics after enabling features
4. **Document Dependencies**: Note which features depend on each other
5. **Plan Rollback**: Have a rollback plan before enabling features
6. **Gradual Rollout**: Enable features one at a time in production
7. **Clean Up**: Remove feature flags once features are stable and proven

## Troubleshooting

### Feature flag not working

1. Check environment variable is set correctly
2. Verify spelling matches exactly (case-sensitive)
3. Check logs for feature flag status on startup
4. For frontend, check browser console for API fetch errors

### Backend logs feature flag status

On startup, the backend logs current feature flag configuration:

```
INFO - Environment: staging
INFO - Feature Flags:
INFO -   ENABLE_CAR_NUMBER: True
INFO -   ENABLE_PART_CATEGORIES: True
INFO -   ENABLE_TG_ADMIN_NOTIFS: True
INFO -   ENABLE_TG_MECH_NOTIFS: True
INFO -   ENABLE_MECH_I18N: True
INFO -   ENABLE_UI_REFRESH: True
```

### Frontend not reflecting backend flags

1. Check that `fetchFeatureFlags()` is called on app initialization
2. Verify API endpoint is accessible
3. Check browser console for fetch errors
4. Ensure CORS is properly configured

## Examples

### Example 1: Enable car number field in production

```bash
# In .env
ENVIRONMENT=production
ENABLE_CAR_NUMBER=true

# Restart backend
# Frontend will fetch updated flag on next load
```

### Example 2: Test new UI in staging only

```bash
# In .env
ENVIRONMENT=staging
ENABLE_UI_REFRESH=true

# Production still has it OFF by default
```

### Example 3: Disable notifications temporarily

```bash
# In .env
ENABLE_TG_ADMIN_NOTIFS=false
ENABLE_TG_MECH_NOTIFS=false

# Restart backend
# Notifications are now disabled
```

## Support

For questions or issues with feature flags, please refer to:
- Backend config: `felix_hub/backend/config.py`
- Frontend config: `felix_hub/frontend/src/config/env.ts`
- Environment examples: `.env.example`
