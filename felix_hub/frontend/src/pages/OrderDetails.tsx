import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'sonner';
import { AxiosError } from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import api from '@/lib/api';
import type { Order } from '@/types';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale/ru';
import { ArrowLeft } from 'lucide-react';

export default function OrderDetails() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  const fetchOrder = useCallback(async () => {
    try {
      const response = await api.get<Order>(`/mechanic/orders/${id}`);
      setOrder(response.data);
    } catch (error) {
      if (error instanceof AxiosError && error.response?.data?.message) {
        toast.error(error.response.data.message);
      } else {
        toast.error('Ошибка загрузки заказа');
      }
      navigate('/mechanic/dashboard');
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => {
    if (!id) return;
    fetchOrder();
  }, [id, fetchOrder]);

  const updateStatus = async (newStatus: Order['status']) => {
    if (!order) return;
    setUpdating(true);
    try {
      const response = await api.patch<Order>(`/mechanic/orders/${order.id}/status`, {
        status: newStatus,
      });
      setOrder(response.data);
      toast.success('Статус обновлен');
    } catch (error) {
      if (error instanceof AxiosError && error.response?.data?.message) {
        toast.error(error.response.data.message);
      } else {
        toast.error('Ошибка обновления статуса');
      }
    } finally {
      setUpdating(false);
    }
  };

  const getStatusVariant = (status: Order['status']) => {
    switch (status) {
      case 'новый':
        return 'default';
      case 'в работе':
        return 'secondary';
      case 'готов':
        return 'outline';
      case 'выдан':
        return 'outline';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Загрузка...</p>
      </div>
    );
  }

  if (!order) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/mechanic/dashboard')}
            className="mb-2"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Назад
          </Button>
          <h1 className="text-2xl font-bold">Заказ #{order.id}</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        <Card className="mb-6">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Информация о заказе</CardTitle>
                <CardDescription>
                  Создан: {format(new Date(order.created_at), 'dd MMMM yyyy, HH:mm', { locale: ru })}
                </CardDescription>
              </div>
              <Badge variant={getStatusVariant(order.status)}>
                {order.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">VIN</p>
              <p className="text-lg">{order.vin}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Категория</p>
              <p className="text-lg">{order.category}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Название детали</p>
              <p className="text-lg">{order.part_name}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Тип детали</p>
              <p className="text-lg">{order.part_type}</p>
            </div>
            {order.photo_url && (
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">Фото</p>
                <img
                  src={order.photo_url}
                  alt="Фото заказа"
                  className="max-w-full h-auto rounded-lg"
                />
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Изменить статус</CardTitle>
            <CardDescription>Обновите статус заказа</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button
              className="w-full touch-target"
              variant={order.status === 'в работе' ? 'secondary' : 'default'}
              onClick={() => updateStatus('в работе')}
              disabled={updating || order.status === 'в работе'}
            >
              В работе
            </Button>
            <Button
              className="w-full touch-target"
              variant={order.status === 'готов' ? 'secondary' : 'default'}
              onClick={() => updateStatus('готов')}
              disabled={updating || order.status === 'готов' || order.status === 'выдан'}
            >
              Готов
            </Button>
            <Button
              className="w-full touch-target"
              variant={order.status === 'выдан' ? 'secondary' : 'default'}
              onClick={() => updateStatus('выдан')}
              disabled={updating || order.status === 'выдан'}
            >
              Выдан
            </Button>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
