import { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, Clock as ClockIcon, Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import StatusButtons from '@/components/mechanic/StatusButtons';
import CommentsList from '@/components/mechanic/CommentsList';
import TimeTracker from '@/components/mechanic/TimeTracker';
import CustomItemsSection from '@/components/mechanic/CustomItemsSection';
import { ordersApi, setupPolling } from '@/api/orders';
import type { OrderDetails as OrderDetailsType } from '@/types';

interface OrderDetailsProps {
  orderId: string | number;
  onBack: () => void;
}

const getStatusColor = (status: string): string => {
  const statusLower = status.toLowerCase();
  const colors: Record<string, string> = {
    'новый': 'bg-blue-500 text-white',
    'new': 'bg-blue-500 text-white',
    'в работе': 'bg-yellow-500 text-white',
    'in progress': 'bg-yellow-500 text-white',
    'на паузе': 'bg-gray-500 text-white',
    'paused': 'bg-gray-500 text-white',
    'ожидание запчастей': 'bg-orange-500 text-white',
    'waiting parts': 'bg-orange-500 text-white',
    'завершен': 'bg-green-500 text-white',
    'completed': 'bg-green-500 text-white',
    'отменен': 'bg-red-500 text-white',
    'cancelled': 'bg-red-500 text-white',
  };
  return colors[statusLower] || 'bg-gray-500 text-white';
};

export default function OrderDetails({ orderId, onBack }: OrderDetailsProps) {
  const [order, setOrder] = useState<OrderDetailsType | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchOrderDetails = useCallback(async () => {
    try {
      const data = await ordersApi.fetchOrderDetails(orderId);
      setOrder(data);
    } catch (err: unknown) {
      console.error('Error fetching order details:', err);
      if (loading) {
        toast.error('Ошибка загрузки заказа');
        onBack();
      }
    } finally {
      setLoading(false);
    }
  }, [orderId, loading, onBack]);

  useEffect(() => {
    fetchOrderDetails();
  }, [orderId, fetchOrderDetails]);

  useEffect(() => {
    const cleanup = setupPolling(fetchOrderDetails);
    return cleanup;
  }, [fetchOrderDetails]);

  const handleStatusChange = async (newStatus: string) => {
    try {
      await ordersApi.updateOrderStatus(orderId, newStatus);
      toast.success('Статус обновлен');
      fetchOrderDetails();
    } catch {
      toast.error('Ошибка обновления статуса');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  if (loading) {
    return <div className="p-4">Загрузка...</div>;
  }

  if (!order) {
    return <div className="p-4">Заказ не найден</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-6">
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="px-4 py-3">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={onBack}
              aria-label="Назад к дашборду"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="font-semibold">Заказ #{order.id}</h1>
              <Badge className={getStatusColor(order.work_status)}>
                {order.work_status}
              </Badge>
              <div className="flex items-center gap-1 text-xs text-gray-500 mt-1">
                <ClockIcon className="h-3 w-3" />
                <span>Обновлен: {formatDate(order.updated_at)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container max-w-4xl mx-auto px-4 py-6 space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Информация</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div>
              <span className="text-sm text-gray-600">Клиент:</span>
              <p className="font-medium">{order.mechanic_name}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">
                {order.car_number ? 'Номер автомобиля:' : 'VIN:'}
              </span>
              <p className="font-medium font-mono">
                {order.car_number || order.vin || 'Не указан'}
              </p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Категория:</span>
              <p className="font-medium">{order.category}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Тип:</span>
              <p className="font-medium">{order.part_type}</p>
            </div>
            <div className="pt-2 border-t">
              <span className="text-sm text-gray-600">Создан:</span>
              <p className="text-sm">{formatDate(order.created_at)}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Последнее обновление:</span>
              <p className="text-sm font-medium">{formatDate(order.updated_at)}</p>
            </div>
          </CardContent>
        </Card>

        <StatusButtons
          currentStatus={order.work_status}
          onStatusChange={handleStatusChange}
        />

        <Tabs defaultValue="details" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="details">Детали</TabsTrigger>
            <TabsTrigger value="time">Время</TabsTrigger>
            <TabsTrigger value="comments">
              Комментарии
              {order.comments_count > 0 && (
                <Badge variant="secondary" className="ml-1">
                  {order.comments_count}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="custom">+</TabsTrigger>
          </TabsList>

          <TabsContent value="details" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Запчасти</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="font-medium">{order.part_name}</p>
              </CardContent>
            </Card>

            {order.photo_url && (
              <Card>
                <CardHeader>
                  <CardTitle>Фото</CardTitle>
                </CardHeader>
                <CardContent>
                  <img
                    src={order.photo_url}
                    alt="Order photo"
                    className="w-full rounded-lg"
                  />
                </CardContent>
              </Card>
            )}

            {order.custom_works && order.custom_works.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Дополнительные работы</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {order.custom_works.map((work) => (
                    <div key={work.id} className="border-b pb-2 last:border-0">
                      <p className="font-medium">{work.name}</p>
                      {work.description && (
                        <p className="text-sm text-gray-600">{work.description}</p>
                      )}
                      <div className="flex justify-between text-sm mt-1">
                        <span>{work.price} ₪</span>
                        <span>{work.estimated_time_minutes} мин</span>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            {order.custom_parts && order.custom_parts.length > 0 && (
              <Card className="bg-amber-50 border-amber-500">
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <Package className="h-5 w-5 text-amber-600" />
                    <CardTitle>Дополнительные запчасти</CardTitle>
                    <Badge className="bg-amber-200 text-amber-800">Кастомные</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2">
                  {order.custom_parts.map((part) => (
                    <div key={part.id} className="flex justify-between">
                      <div>
                        <p className="font-medium">{part.name}</p>
                        {part.part_number && (
                          <p className="text-sm text-gray-600">{part.part_number}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{part.price} ₪</p>
                        <p className="text-sm text-gray-600">x{part.quantity}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="time">
            <TimeTracker orderId={order.id} timeLogs={order.time_logs || []} />
          </TabsContent>

          <TabsContent value="comments">
            <CommentsList
              orderId={order.id}
              comments={order.comments || []}
              onCommentAdded={fetchOrderDetails}
            />
          </TabsContent>

          <TabsContent value="custom">
            <CustomItemsSection
              orderId={order.id}
              onItemAdded={fetchOrderDetails}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
