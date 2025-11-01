import { LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import LanguageSwitcher from './LanguageSwitcher';
import { useTranslation } from 'react-i18next';

interface HeaderProps {
  userName?: string;
  onLogout: () => void;
}

export default function Header({ userName, onLogout }: HeaderProps) {
  const { t } = useTranslation();

  return (
    <header className="bg-white border-b sticky top-0 z-50">
      <div className="px-4 py-3 flex items-center justify-between">
        <h1 className="text-lg font-semibold">{t('header.appName')}</h1>
        <div className="flex items-center gap-2">
          {userName && (
            <span className="text-sm text-gray-600 hidden sm:inline">
              {userName}
            </span>
          )}
          <LanguageSwitcher />
          <Button
            variant="ghost"
            size="icon"
            onClick={onLogout}
            className="touch-target"
            title={t('header.logout')}
          >
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
