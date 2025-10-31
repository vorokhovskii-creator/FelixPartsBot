# Render Static Site Deployment - Mechanics Frontend

## Overview

This document describes the deployment of the Felix Hub mechanics frontend to Render as a static site.

## Changes Made

### 1. API Configuration (`felix_hub/frontend/src/lib/api.ts`)

Updated the axios baseURL to use environment variable:

```typescript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});
```

- **Production**: Uses `VITE_API_URL` environment variable
- **Development**: Falls back to `/api` (proxied by Vite dev server)

### 2. Production Environment File (`.env.production`)

Created `felix_hub/frontend/.env.production`:

```env
VITE_API_URL=https://felix-hub-backend.onrender.com/api
```

This file is committed to the repository as it contains non-sensitive configuration.

### 3. Render Configuration (`render.yaml`)

Added static site service configuration:

```yaml
services:
  - type: web
    name: felix-hub-mechanics-frontend
    env: static
    region: frankfurt
    plan: free
    branch: main
    buildCommand: "cd felix_hub/frontend && npm ci && npm run build"
    staticPublishPath: felix_hub/frontend/dist
    autoDeploy: true
    envVars:
      - key: VITE_API_URL
        value: https://felix-hub-backend.onrender.com/api
```

### 4. Documentation Updates

- Updated `DEPLOYMENT.md` with comprehensive frontend deployment instructions
- Updated `felix_hub/frontend/README.md` with environment variables and deployment section

### 5. Bug Fixes

Fixed TypeScript errors in `ErrorBoundary.tsx`:
- Changed to type-only imports for `ErrorInfo` and `ReactNode`
- Replaced `process.env.NODE_ENV` with `import.meta.env.MODE` (Vite standard)

## Deployment Steps

### Automatic (Recommended)

1. Push changes to `main` branch
2. Render automatically deploys from `render.yaml`

### Manual via Render Dashboard

1. Navigate to Render Dashboard
2. **New → Static Site**
3. Connect GitHub repository: `FelixPartsBot`
4. Configure:
   - **Name**: `felix-hub-mechanics-frontend`
   - **Branch**: `main`
   - **Build Command**: `cd felix_hub/frontend && npm ci && npm run build`
   - **Publish Directory**: `felix_hub/frontend/dist`
   - **Auto-Deploy**: Yes
5. Add Environment Variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://felix-hub-backend.onrender.com/api`

## Verification Checklist

After deployment, verify the following:

### Basic Functionality
- [ ] Static site is accessible at the Render URL
- [ ] `/mechanic/login` page loads without errors
- [ ] All static assets (CSS, JS) load correctly
- [ ] No console errors on page load

### API Integration
- [ ] Network requests go to `https://felix-hub-backend.onrender.com/api`
- [ ] No CORS errors in console
- [ ] Can log in with mechanic credentials
- [ ] Dashboard loads and displays orders

### Smoke Test Flow
- [ ] **Login**: Enter credentials and authenticate
- [ ] **Dashboard**: View list of orders
- [ ] **Order Details**: Click on an order to view details
- [ ] **Status Change**: Update order status
- [ ] **Comment**: Add a comment to an order
- [ ] **Time Tracker**: Start and stop work timer
- [ ] **Logout**: Log out successfully

### Performance
- [ ] Initial page load < 3s
- [ ] API responses < 2s
- [ ] No mixed content warnings (HTTP/HTTPS)

## CORS Configuration

If CORS errors occur, ensure the backend has the correct configuration:

### Option 1: Environment Variable (Recommended)

Add to Render backend environment variables:
```
FRONTEND_ORIGIN=https://felix-hub-mechanics-frontend.onrender.com
```

### Option 2: Code Configuration

Update `felix_hub/backend/app.py`:

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://felix-hub-mechanics-frontend.onrender.com",
            "http://localhost:5173"  # for local development
        ],
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PATCH", "DELETE"]
    }
})
```

## Troubleshooting

### Build Fails

**Check**:
- Node.js version compatibility (should use Node 18+)
- npm dependencies are up to date
- Build logs in Render dashboard

**Fix**:
```bash
cd felix_hub/frontend
npm ci
npm run build
```

### API Requests Fail

**Check**:
- Backend is running at `https://felix-hub-backend.onrender.com`
- `VITE_API_URL` environment variable is set correctly
- CORS is configured on backend

**Debug**:
- Open browser DevTools → Network tab
- Check request URLs and responses
- Look for CORS errors in console

### Routes Not Working (404)

**Check**:
- All client-side routes should be handled by `index.html`
- Render static sites automatically handle SPAs

**Fix**: Render should handle this automatically, but verify in the Render dashboard that:
- Publish directory is `felix_hub/frontend/dist`
- `index.html` exists in the dist directory

## Build Output

The production build creates:

```
felix_hub/frontend/dist/
├── index.html              # Entry point
├── vite.svg               # Favicon
└── assets/
    ├── index-[hash].js    # JavaScript bundle (~500KB)
    └── index-[hash].css   # Stylesheet bundle (~28KB)
```

## Environment Variables Reference

| Variable | Purpose | Value |
|----------|---------|-------|
| `VITE_API_URL` | Backend API base URL | `https://felix-hub-backend.onrender.com/api` |

## Performance Considerations

The current bundle size is ~500KB (156KB gzipped). Consider:
- Code splitting with dynamic imports
- Lazy loading routes
- Manual chunks configuration

For now, the bundle size is acceptable for the mechanic dashboard use case.

## Next Steps

1. Monitor deployment in Render dashboard
2. Test all mechanic workflows
3. Set up error tracking (e.g., Sentry)
4. Configure custom domain (optional)
5. Set up monitoring/alerting

## Related Documentation

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Full deployment guide
- [felix_hub/frontend/README.md](./felix_hub/frontend/README.md) - Frontend documentation
- [Render Static Site Docs](https://render.com/docs/static-sites)
