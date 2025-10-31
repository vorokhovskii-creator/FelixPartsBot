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

No environment variables are required for development. The API proxy is configured in `vite.config.ts`.
