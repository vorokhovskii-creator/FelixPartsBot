# Flask Integration Guide

This guide explains how to integrate the React frontend with the Flask backend.

## Development Setup

### 1. Run Both Servers

In development, run both servers separately:

**Terminal 1 - Flask Backend:**
```bash
cd felix_hub/backend
python app.py
# Runs on http://localhost:5000
```

**Terminal 2 - React Frontend:**
```bash
cd felix_hub/frontend
npm run dev
# Runs on http://localhost:3000
```

The Vite dev server is configured to proxy API requests from `/api/*` to `http://localhost:5000`.

## Production Setup

### 1. Build the React App

```bash
cd felix_hub/frontend
npm run build
```

This creates optimized static files in `felix_hub/frontend/dist/`.

### 2. Update Flask to Serve React App

Add the following routes to your `felix_hub/backend/app.py`:

```python
import os
from flask import send_from_directory

# Serve React static files
@app.route('/mechanic', defaults={'path': ''})
@app.route('/mechanic/<path:path>')
def serve_mechanic_app(path):
    """Serve the React mechanic frontend"""
    dist_dir = os.path.join(os.path.dirname(__file__), '../frontend/dist')
    
    if path and os.path.exists(os.path.join(dist_dir, path)):
        return send_from_directory(dist_dir, path)
    
    # For React Router - serve index.html for all routes
    return send_from_directory(dist_dir, 'index.html')
```

### 3. CORS Configuration (Development Only)

If you need CORS during development, install flask-cors:

```bash
pip install flask-cors
```

Then in `app.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
```

**Note:** Remove or restrict CORS in production!

## API Endpoints

The React app expects the following API endpoints:

### Authentication
- `POST /api/mechanic/login` - Login mechanic with phone number
  - Request: `{ "phone": "+7..." }`
  - Response: `{ "token": "...", "mechanic": {...} }`

### Orders
- `GET /api/mechanic/orders` - Get all orders for authenticated mechanic
  - Headers: `Authorization: Bearer <token>`
  - Response: `[{ "id": 1, "vin": "...", ... }]`

- `GET /api/mechanic/orders/:id` - Get single order details
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ "id": 1, "vin": "...", ... }`

- `PATCH /api/mechanic/orders/:id/status` - Update order status
  - Headers: `Authorization: Bearer <token>`
  - Request: `{ "status": "в работе" | "готов" | "выдан" }`
  - Response: `{ "id": 1, "status": "...", ... }`

## Deployment

### Option 1: Serve from Flask (Recommended)

1. Build the React app: `npm run build`
2. Deploy Flask app with the `dist/` folder
3. Flask serves both API and frontend

### Option 2: Separate Hosting

1. Build the React app: `npm run build`
2. Deploy `dist/` folder to static hosting (Vercel, Netlify, etc.)
3. Update API base URL in React app to point to Flask server
4. Configure CORS in Flask for the frontend domain

## File Structure

```
felix_hub/
├── backend/
│   ├── app.py          # Add React serving routes here
│   └── ...
└── frontend/
    ├── dist/           # Built React app (after npm run build)
    ├── src/
    └── ...
```

## Environment Variables

For production, you may want to configure the API URL:

Create `felix_hub/frontend/.env.production`:

```env
VITE_API_URL=https://your-api-domain.com
```

Then update `src/lib/api.ts`:

```typescript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  // ...
});
```

## Testing the Integration

1. Build the frontend: `cd felix_hub/frontend && npm run build`
2. Start Flask: `cd felix_hub/backend && python app.py`
3. Visit: `http://localhost:5000/mechanic`
4. You should see the React login page

## Troubleshooting

### React Router 404s in Production

Make sure Flask returns `index.html` for all `/mechanic/*` routes (see step 2 above).

### API Requests Failing

- Check that API endpoints start with `/api/`
- Verify authentication token is being sent
- Check browser console for CORS errors

### Static Assets Not Loading

- Ensure the `dist/` folder exists after building
- Check file paths in Flask `send_from_directory()`
- Verify Flask can access the `dist/` directory
