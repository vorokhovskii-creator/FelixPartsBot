import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { useEffect, lazy, Suspense } from 'react';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';
import MechanicLayout from './components/mechanic/MechanicLayout';

const MechanicLogin = lazy(() => import('./pages/MechanicLogin'));
const MechanicDashboard = lazy(() => import('./pages/MechanicDashboard'));
const OrderDetails = lazy(() => import('./pages/OrderDetails'));
const MechanicTimeHistory = lazy(() => import('./pages/MechanicTimeHistory'));
const MechanicProfile = lazy(() => import('./pages/MechanicProfile'));

function DeeplinkHandler() {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get('token');
    const orderId = location.pathname.match(/\/mechanic\/orders\/(\d+)/)?.[1];

    // If we have a token but no auth, redirect to login with params
    if (token && !localStorage.getItem('mechanic_token')) {
      const redirectParams = new URLSearchParams();
      redirectParams.set('token', token);
      if (orderId) {
        redirectParams.set('order', orderId);
      }
      navigate(`/mechanic/login?${redirectParams.toString()}`, { replace: true });
    }
  }, [location, navigate]);

  return null;
}

function LoadingFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Загрузка...</p>
      </div>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <DeeplinkHandler />
        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            <Route path="/" element={<Navigate to="/mechanic/login" replace />} />
            <Route path="/mechanic/login" element={<MechanicLogin />} />
            <Route
              path="/mechanic"
              element={
                <ProtectedRoute>
                  <MechanicLayout />
                </ProtectedRoute>
              }
            >
              <Route path="dashboard" element={<MechanicDashboard />} />
              <Route path="orders/:id" element={<OrderDetails />} />
              <Route path="time" element={<MechanicTimeHistory />} />
              <Route path="profile" element={<MechanicProfile />} />
            </Route>
          </Routes>
        </Suspense>
        <Toaster position="top-center" />
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
