import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import OrderItem from './OrderItem';
import { ordersApi, setupPolling } from '@/api/orders';
import type { Order } from '@/types';

interface OrdersListProps {
  filter?: string;
  onOrderClick: (orderId: number) => void;
}

export default function OrdersList({ filter = 'all', onOrderClick }: OrdersListProps) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrders = useCallback(async () => {
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const data = await ordersApi.fetchOrders(params);
      setOrders(data);
      setError(null);
    } catch (err: unknown) {
      console.error('Error fetching orders:', err);
      const error = err as { response?: { data?: { error?: string } } };
      const message = error.response?.data?.error || 'Ошибка загрузки заказов';
      setError(message);
      if (loading) {
        toast.error(message);
      }
    } finally {
      setLoading(false);
    }
  }, [filter, loading]);

  useEffect(() => {
    setLoading(true);
    fetchOrders();
  }, [filter, fetchOrders]);

  useEffect(() => {
    const cleanup = setupPolling(fetchOrders);
    return cleanup;
  }, [fetchOrders]);

  if (loading && orders.length === 0) {
    return <div className="text-center py-8 text-gray-500">Загрузка...</div>;
  }

  if (error && !loading && orders.length === 0) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="p-4 flex items-center gap-2 text-red-800">
          <AlertCircle className="h-5 w-5" />
          <span>{error}</span>
        </CardContent>
      </Card>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        Нет заказов
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {orders.map((order) => (
        <OrderItem key={order.id} order={order} onClick={onOrderClick} />
      ))}
    </div>
  );
}
