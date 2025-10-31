import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { useEffect } from 'react';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';
import MechanicLayout from './components/mechanic/MechanicLayout';
import MechanicLogin from './pages/MechanicLogin';
import MechanicDashboard from './pages/MechanicDashboard';
import OrderDetails from './pages/OrderDetails';
import MechanicTimeHistory from './pages/MechanicTimeHistory';
import MechanicProfile from './pages/MechanicProfile';

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

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <DeeplinkHandler />
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
        <Toaster position="top-center" />
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
