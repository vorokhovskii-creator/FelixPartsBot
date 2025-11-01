import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Clock } from 'lucide-react';
import type { Order } from '@/types';
import type { BadgeProps } from '@/components/ui/badge';

interface OrderItemProps {
  order: Order;
  onClick: (orderId: number) => void;
}

const getStatusVariant = (status: string): BadgeProps['variant'] => {
  const statusLower = status.toLowerCase();
  const variants: Record<string, BadgeProps['variant']> = {
    'новый': 'info',
    'new': 'info',
    'в работе': 'warning',
    'in progress': 'warning',
    'на паузе': 'secondary',
    'paused': 'secondary',
    'ожидание запчастей': 'warning',
    'waiting parts': 'warning',
    'завершен': 'success',
    'completed': 'success',
    'отменен': 'error',
    'cancelled': 'error',
  };
  return variants[statusLower] || 'default';
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
      className="cursor-pointer hover:shadow-lg transition-all"
      onClick={() => onClick(order.id)}
    >
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="font-bold text-lg mb-1">
              Заказ #{order.id}
            </h3>
            <p className="text-sm text-muted-foreground">
              {order.car_number || order.vin || 'Номер не указан'}
            </p>
          </div>
          <Badge variant={getStatusVariant(order.work_status)}>
            {order.work_status}
          </Badge>
        </div>

        <div className="space-y-2">
          <p className="text-sm">
            <span className="font-semibold text-foreground">Категория:</span>{' '}
            <span className="text-muted-foreground">{order.category}</span>
          </p>
          <p className="text-sm">
            <span className="font-semibold text-foreground">Запчасть:</span>{' '}
            <span className="text-muted-foreground">{order.part_name}</span>
          </p>
          <p className="text-xs text-muted-foreground">
            Создан: {formatDate(order.created_at)}
          </p>
          <p className="text-xs text-muted-foreground">
            Обновлен: {formatDate(order.updated_at)}
          </p>
        </div>

        {order.total_time_minutes > 0 && (
          <div className="mt-3 flex items-center text-sm font-medium text-primary">
            <Clock className="h-4 w-4 mr-1.5" />
            {Math.floor(order.total_time_minutes / 60)}ч {order.total_time_minutes % 60}м
          </div>
        )}
      </CardContent>
    </Card>
  );
}
