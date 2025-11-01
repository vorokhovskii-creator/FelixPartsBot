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

export default function MechanicDashboard() {
  const [stats, setStats] = useState<MechanicStats | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchStats = useCallback(async () => {
    try {
      const response = await api.get('/mechanic/stats');
      setStats(response.data);
      setError(null);
    } catch (err: unknown) {
      console.error('Error fetching stats:', err);
      const error = err as { response?: { data?: { error?: string } } };
      const message = error.response?.data?.error || 'Ошибка загрузки статистики';
      setError(message);
      if (loading) {
        toast.error(message);
      }
    }
  }, [loading]);

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
        className="w-full mb-6"
        onClick={() => navigate('/mechanic/orders/new')}
      >
        <Plus className="h-5 w-5 mr-2" />
        Создать заказ
      </Button>

      {/* Статистика */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col items-center text-center">
              <Wrench className="h-8 w-8 text-blue-600 mb-2" />
              <p className="text-2xl font-bold">{stats?.active_orders || 0}</p>
              <p className="text-xs text-gray-600">В работе</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col items-center text-center">
              <CheckCircle className="h-8 w-8 text-green-600 mb-2" />
              <p className="text-2xl font-bold">{stats?.completed_today || 0}</p>
              <p className="text-xs text-gray-600">Сегодня</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col items-center text-center">
              <Clock className="h-8 w-8 text-orange-600 mb-2" />
              <p className="text-2xl font-bold">
                {Math.floor((stats?.time_today_minutes || 0) / 60)}ч
              </p>
              <p className="text-xs text-gray-600">Времени</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Фильтры */}
      <Tabs value={filter} onValueChange={setFilter} className="mb-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all">Все</TabsTrigger>
          <TabsTrigger value="новый">Новые</TabsTrigger>
          <TabsTrigger value="в работе">В работе</TabsTrigger>
          <TabsTrigger value="завершен">Готовые</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Список заказов */}
      {error && (
        <Card className="border-red-200 bg-red-50 mb-4">
          <CardContent className="p-4 flex items-center gap-2 text-red-800">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
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
