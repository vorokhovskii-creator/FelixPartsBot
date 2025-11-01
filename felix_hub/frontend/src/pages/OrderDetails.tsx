import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Phone } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import api from '@/lib/api';
import StatusButtons from '@/components/mechanic/StatusButtons';
import CommentsList from '@/components/mechanic/CommentsList';
import TimeTracker from '@/components/mechanic/TimeTracker';
import CustomItemsSection from '@/components/mechanic/CustomItemsSection';
import type { OrderDetails } from '@/types';

export default function OrderDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState<OrderDetails | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrderDetails();
  }, [id]);

  const fetchOrderDetails = async () => {
    try {
      const response = await api.get(`/mechanic/orders/${id}`);
      setOrder(response.data);
    } catch (error) {
      toast.error('Ошибка загрузки заказа');
      navigate('/mechanic/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    try {
      await api.patch(`/mechanic/orders/${id}/status`, { status: newStatus });
      toast.success('Статус обновлен');
      fetchOrderDetails();
    } catch (error) {
      toast.error('Ошибка обновления статуса');
    }
  };

  if (loading) {
    return <div className="p-4">Загрузка...</div>;
  }

  if (!order) {
    return <div className="p-4">Заказ не найден</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-6">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate('/mechanic/dashboard')}
              aria-label="Назад к дашборду"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="font-semibold">Заказ #{order.id}</h1>
              <Badge className="mt-1">{order.work_status}</Badge>
            </div>
          </div>
          
          {order.phone && (
            <Button
              variant="outline"
              size="icon"
              asChild
              aria-label="Позвонить клиенту"
            >
              <a href={`tel:${order.phone}`}>
                <Phone className="h-5 w-5" />
              </a>
            </Button>
          )}
        </div>
      </div>

      <div className="container max-w-4xl mx-auto px-4 py-6 space-y-4">
        {/* Информация о клиенте */}
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
          </CardContent>
        </Card>

        {/* Управление статусом */}
        <StatusButtons
          currentStatus={order.work_status}
          onStatusChange={handleStatusChange}
        />

        {/* Табы */}
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

          {/* Детали заказа */}
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

            {/* Кастомные работы */}
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

            {/* Кастомные запчасти */}
            {order.custom_parts && order.custom_parts.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Дополнительные запчасти</CardTitle>
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

          {/* Учет времени */}
          <TabsContent value="time">
            <TimeTracker orderId={order.id} timeLogs={order.time_logs || []} />
          </TabsContent>

          {/* Комментарии */}
          <TabsContent value="comments">
            <CommentsList
              orderId={order.id}
              comments={order.comments || []}
              onCommentAdded={fetchOrderDetails}
            />
          </TabsContent>

          {/* Добавление кастомных позиций */}
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
