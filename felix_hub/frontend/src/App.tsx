import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import ProtectedRoute from './components/ProtectedRoute';
import MechanicLayout from './components/mechanic/MechanicLayout';
import MechanicLogin from './pages/MechanicLogin';
import MechanicDashboard from './pages/MechanicDashboard';
import OrderDetails from './pages/OrderDetails';
import MechanicTimeHistory from './pages/MechanicTimeHistory';

function App() {
  return (
    <BrowserRouter>
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
          <Route path="profile" element={<div className="p-4 text-center">Профиль (в разработке)</div>} />
        </Route>
      </Routes>
      <Toaster position="top-center" />
    </BrowserRouter>
  );
}

export default App;
