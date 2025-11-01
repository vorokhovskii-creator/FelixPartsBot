import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Clock, CheckCircle, Wrench, AlertCircle, Plus } from 'lucide-react';
import { toast } from 'sonner';
import { DashboardSkeleton } from '@/components/LoadingSkeleton';
import OrdersList from '@/features/orders/OrdersList';
import { setupPolling } from '@/api/orders';
import api from '@/lib/api';
import type { MechanicStats } from '@/types';
import { useTranslation } from 'react-i18next';

export default function MechanicDashboard() {
  const [stats, setStats] = useState<MechanicStats | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const fetchStats = useCallback(async () => {
    try {
      const response = await api.get('/mechanic/stats');
      setStats(response.data);
      setError(null);
    } catch (err: unknown) {
      console.error('Error fetching stats:', err);
      const error = err as { response?: { data?: { error?: string } } };
      const message = error.response?.data?.error || t('dashboard.errors.loadingStats');
      setError(message);
      if (loading) {
        toast.error(message);
      }
    }
  }, [loading, t]);

  useEffect(() => {
    fetchStats();
    setLoading(false);
  }, [fetchStats]);

  useEffect(() => {
    const cleanup = setupPolling(fetchStats);
    return cleanup;
  }, [fetchStats]);

  if (loading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="container max-w-4xl mx-auto px-4 py-6">
      {/* Кнопка создания заказа */}
      <Button 
        className="w-full mb-6 h-12"
        onClick={() => navigate('/mechanic/orders/new')}
      >
        <Plus className="h-5 w-5" />
        {t('dashboard.createOrder')}
      </Button>

      {/* Статистика */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <Card className="border-l-4 border-l-primary">
          <CardContent className="p-4">
            <div className="flex flex-col items-center text-center">
              <Wrench className="h-9 w-9 text-primary mb-3" />
              <p className="text-3xl font-bold text-foreground">{stats?.active_orders || 0}</p>
              <p className="text-xs text-muted-foreground font-medium mt-1">{t('dashboard.stats.active')}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-success">
          <CardContent className="p-4">
            <div className="flex flex-col items-center text-center">
              <CheckCircle className="h-9 w-9 text-success mb-3" />
              <p className="text-3xl font-bold text-foreground">{stats?.completed_today || 0}</p>
              <p className="text-xs text-muted-foreground font-medium mt-1">{t('dashboard.stats.completed')}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-warning">
          <CardContent className="p-4">
            <div className="flex flex-col items-center text-center">
              <Clock className="h-9 w-9 text-warning mb-3" />
              <p className="text-3xl font-bold text-foreground">
                {Math.floor((stats?.time_today_minutes || 0) / 60)}ч
              </p>
              <p className="text-xs text-muted-foreground font-medium mt-1">{t('dashboard.stats.time')}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Фильтры */}
      <Tabs value={filter} onValueChange={setFilter} className="mb-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all">{t('dashboard.filters.all')}</TabsTrigger>
          <TabsTrigger value="новый">{t('dashboard.filters.new')}</TabsTrigger>
          <TabsTrigger value="в работе">{t('dashboard.filters.inProgress')}</TabsTrigger>
          <TabsTrigger value="завершен">{t('dashboard.filters.completed')}</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Список заказов */}
      {error && (
        <Card className="border-error/50 bg-error/10 mb-4">
          <CardContent className="p-4 flex items-center gap-3">
            <AlertCircle className="h-5 w-5 text-error flex-shrink-0" />
            <span className="text-sm font-medium text-error-foreground">{error}</span>
          </CardContent>
        </Card>
      )}
      <OrdersList
        filter={filter}
        onOrderClick={(orderId) => navigate(`/mechanic/orders/${orderId}`)}
      />
    </div>
  );
}
