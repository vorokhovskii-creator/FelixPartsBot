import { LogOut, Wrench } from 'lucide-react';
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
    <header className="bg-white border-b sticky top-0 z-50 shadow-sm">
      <div className="px-4 py-3 flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-accent">
            <Wrench className="h-5 w-5 text-white" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-lg font-bold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              {t('header.appName')}
            </h1>
            <p className="text-xs text-muted-foreground hidden sm:block">
              {t('header.tagline')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {userName && (
            <span className="text-sm text-muted-foreground hidden sm:inline px-3 py-1.5 bg-secondary rounded-full">
              {userName}
            </span>
          )}
          <LanguageSwitcher />
          <Button
            variant="ghost"
            size="icon"
            onClick={onLogout}
            className="touch-target rounded-full hover:bg-secondary"
            title={t('header.logout')}
          >
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
