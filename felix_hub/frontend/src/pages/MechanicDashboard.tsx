import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Clock, CheckCircle, Wrench, AlertCircle, Plus } from 'lucide-react';
import { toast } from 'sonner';
import { DashboardSkeleton } from '@/components/LoadingSkeleton';
import api from '@/lib/api';
import type { Order, MechanicStats } from '@/types';

export default function MechanicDashboard() {
  const [orders, setOrders] = useState<Order[]>([]);
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
    } catch (error: any) {
      console.error('Error fetching stats:', error);
      const message = error.response?.data?.error || 'Ошибка загрузки статистики';
      setError(message);
      toast.error(message);
    }
  }, []);

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const response = await api.get('/mechanic/orders', { params });
      setOrders(response.data);
    } catch (error: any) {
      console.error('Error fetching orders:', error);
      const message = error.response?.data?.error || 'Ошибка загрузки заказов';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchStats();
    fetchOrders();
  }, [fetchStats, fetchOrders]);

  const getStatusColor = (status: string) => {
    const colors = {
      'новый': 'bg-blue-100 text-blue-800',
      'в работе': 'bg-yellow-100 text-yellow-800',
      'на паузе': 'bg-gray-100 text-gray-800',
      'завершен': 'bg-green-100 text-green-800',
    };
    return colors[status as keyof typeof colors] || '';
  };

  if (loading && orders.length === 0) {
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
      <div className="space-y-3">
        {error && !loading && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="p-4 flex items-center gap-2 text-red-800">
              <AlertCircle className="h-5 w-5" />
              <span>{error}</span>
            </CardContent>
          </Card>
        )}
        {loading ? (
          <div className="text-center py-8 text-gray-500">Загрузка...</div>
        ) : orders.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Нет заказов
          </div>
        ) : (
          orders.map((order) => (
            <Card
              key={order.id}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => navigate(`/mechanic/orders/${order.id}`)}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-semibold text-lg">
                      Заказ #{order.id}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {order.car_number || order.vin || 'Номер не указан'}
                    </p>
                  </div>
                  <Badge className={getStatusColor(order.work_status)}>
                    {order.work_status}
                  </Badge>
                </div>

                <div className="space-y-1">
                  <p className="text-sm">
                    <span className="font-medium">Категория:</span> {order.category}
                  </p>
                  <p className="text-sm">
                    <span className="font-medium">Запчасть:</span> {order.part_name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(order.created_at).toLocaleString('ru-RU')}
                  </p>
                </div>

                {order.total_time_minutes > 0 && (
                  <div className="mt-2 flex items-center text-sm text-gray-600">
                    <Clock className="h-4 w-4 mr-1" />
                    {Math.floor(order.total_time_minutes / 60)}ч {order.total_time_minutes % 60}м
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
