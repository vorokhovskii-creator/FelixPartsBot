import { Outlet, useNavigate } from 'react-router-dom';
import { Home, Clock, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTranslation } from 'react-i18next';
import Header from '@/layout/Header';

export default function MechanicLayout() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  
  const getMechanic = () => {
    try {
      const mechanicData = localStorage.getItem('mechanic');
      if (!mechanicData) return { name: t('profile.mechanic') };
      return JSON.parse(mechanicData);
    } catch (error) {
      console.error('Error parsing mechanic data:', error);
      return { name: t('profile.mechanic') };
    }
  };
  
  const mechanic = getMechanic();

  const handleLogout = () => {
    localStorage.removeItem('mechanic_token');
    localStorage.removeItem('mechanic');
    navigate('/mechanic/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header userName={mechanic.name} onLogout={handleLogout} />

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
            <span className="text-xs">{t('navigation.orders')}</span>
          </Button>
          
          <Button
            variant="ghost"
            className="flex-col h-auto py-2"
            onClick={() => navigate('/mechanic/time')}
          >
            <Clock className="h-6 w-6 mb-1" />
            <span className="text-xs">{t('navigation.time')}</span>
          </Button>
          
          <Button
            variant="ghost"
            className="flex-col h-auto py-2"
            onClick={() => navigate('/mechanic/profile')}
          >
            <User className="h-6 w-6 mb-1" />
            <span className="text-xs">{t('navigation.profile')}</span>
          </Button>
        </div>
      </nav>
    </div>
  );
}
