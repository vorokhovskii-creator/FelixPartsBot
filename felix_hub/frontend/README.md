# Felix Hub - Mechanic Frontend

React + Vite + TypeScript frontend for the Felix Hub mechanic module.

## Tech Stack

- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **TypeScript** - Type safety
- **Tailwind CSS v4** - Styling
- **shadcn/ui** - UI component library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Sonner** - Toast notifications
- **date-fns** - Date formatting

## Getting Started

### Install dependencies

```bash
npm install
```

### Development

Start the dev server on port 3000:

```bash
npm run dev
```

The dev server includes proxy configuration to forward `/api/*` requests to the Flask backend at `http://localhost:5000`.

### Build for Production

```bash
npm run build
```

This creates optimized static files in the `dist/` directory that can be served by Flask.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── ui/          # shadcn/ui components
│   └── mechanic/    # Mechanic-specific components
├── pages/
│   ├── MechanicLogin.tsx
│   ├── MechanicDashboard.tsx
│   └── OrderDetails.tsx
├── lib/
│   ├── api.ts       # Axios API client
│   └── utils.ts     # Utility functions
├── hooks/           # Custom React hooks
├── types/           # TypeScript type definitions
├── App.tsx          # Main app component
└── main.tsx         # App entry point
```

## API Integration

The app communicates with the Flask backend through the `/api` proxy. Authentication tokens are stored in `localStorage` and automatically attached to requests via Axios interceptors.

## Mobile-First Design

The UI is designed mobile-first with touch-friendly targets (min 44x44px) and responsive layouts using Tailwind CSS.

## Adding Components

To add new shadcn/ui components:

```bash
npx shadcn-ui@latest add [component-name]
```

Example:
```bash
npx shadcn-ui@latest add dialog
```

## Environment Variables

### Development

No environment variables are required for development. The API proxy is configured in `vite.config.ts`.

### Production

For production deployment, the app uses environment variables to configure the API URL:

- `VITE_API_URL` - Backend API base URL (e.g., `https://felix-hub-backend.onrender.com/api`)

The `.env.production` file is included in the repository with the production API URL:

```env
VITE_API_URL=https://felix-hub-backend.onrender.com/api
```

## Deployment

### Render Static Site

The frontend is deployed as a static site on Render.com. The configuration is in `render.yaml` at the repository root.

#### Automatic Deployment

When you push to the `main` branch, Render automatically:
1. Runs `npm ci && npm run build`
2. Publishes the `dist/` directory

#### Manual Deployment via Render Dashboard

1. **New → Static Site**
2. **Connect repository**: FelixPartsBot
3. **Configure**:
   - Name: `felix-hub-mechanics-frontend`
   - Branch: `main`
   - Build Command: `cd felix_hub/frontend && npm ci && npm run build`
   - Publish Directory: `felix_hub/frontend/dist`
   - Auto-Deploy: Yes
4. **Environment Variables**:
   - `VITE_API_URL`: `https://felix-hub-backend.onrender.com/api`

#### Verify Deployment

1. Visit `https://[your-site].onrender.com/mechanic/login`
2. Check that:
   - ✅ All pages load without errors
   - ✅ API requests go to the correct backend URL
   - ✅ No CORS errors in console
   - ✅ Login and dashboard work correctly

### Local Production Build

To test the production build locally:

```bash
npm run build
npm run preview
```

The preview server will serve the production build at `http://localhost:4173`.
