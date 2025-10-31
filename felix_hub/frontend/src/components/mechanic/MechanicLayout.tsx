import { Outlet, useNavigate } from 'react-router-dom';
import { Home, Clock, User, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function MechanicLayout() {
  const navigate = useNavigate();
  const mechanic = JSON.parse(localStorage.getItem('mechanic') || '{}');

  const handleLogout = () => {
    localStorage.removeItem('mechanic_token');
    localStorage.removeItem('mechanic');
    navigate('/mechanic/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="px-4 py-3 flex items-center justify-between">
          <h1 className="text-lg font-semibold">Felix Hub</h1>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600 hidden sm:inline">
              {mechanic.name}
            </span>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              className="touch-target"
            >
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="pb-20 md:pb-4">
        <Outlet />
      </main>

      {/* Bottom Navigation (mobile only) */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t md:hidden">
        <div className="flex justify-around py-2">
          <Button
            variant="ghost"
            className="flex-col h-auto py-2"
            onClick={() => navigate('/mechanic/dashboard')}
          >
            <Home className="h-6 w-6 mb-1" />
            <span className="text-xs">Заказы</span>
          </Button>
          
          <Button
            variant="ghost"
            className="flex-col h-auto py-2"
            onClick={() => navigate('/mechanic/time')}
          >
            <Clock className="h-6 w-6 mb-1" />
            <span className="text-xs">Время</span>
          </Button>
          
          <Button
            variant="ghost"
            className="flex-col h-auto py-2"
            onClick={() => navigate('/mechanic/profile')}
          >
            <User className="h-6 w-6 mb-1" />
            <span className="text-xs">Профиль</span>
          </Button>
        </div>
      </nav>
    </div>
  );
}
