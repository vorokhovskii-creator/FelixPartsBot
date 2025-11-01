import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Clock } from 'lucide-react';
import type { Order } from '@/types';

interface OrderItemProps {
  order: Order;
  onClick: (orderId: number) => void;
}

const getStatusColor = (status: string): string => {
  const statusLower = status.toLowerCase();
  const colors: Record<string, string> = {
    'новый': 'bg-blue-500 text-white hover:bg-blue-600',
    'new': 'bg-blue-500 text-white hover:bg-blue-600',
    'в работе': 'bg-yellow-500 text-white hover:bg-yellow-600',
    'in progress': 'bg-yellow-500 text-white hover:bg-yellow-600',
    'на паузе': 'bg-gray-500 text-white hover:bg-gray-600',
    'paused': 'bg-gray-500 text-white hover:bg-gray-600',
    'ожидание запчастей': 'bg-orange-500 text-white hover:bg-orange-600',
    'waiting parts': 'bg-orange-500 text-white hover:bg-orange-600',
    'завершен': 'bg-green-500 text-white hover:bg-green-600',
    'completed': 'bg-green-500 text-white hover:bg-green-600',
    'отменен': 'bg-red-500 text-white hover:bg-red-600',
    'cancelled': 'bg-red-500 text-white hover:bg-red-600',
  };
  return colors[statusLower] || 'bg-gray-500 text-white';
};

export default function OrderItem({ order, onClick }: OrderItemProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Card
      className="cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => onClick(order.id)}
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
            Создан: {formatDate(order.created_at)}
          </p>
          <p className="text-xs text-gray-500">
            Обновлен: {formatDate(order.updated_at)}
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
  );
}
