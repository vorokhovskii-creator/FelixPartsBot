import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import api from '@/lib/api';
import type { Order, Mechanic } from '@/types';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

export default function MechanicDashboard() {
  const navigate = useNavigate();
  const [orders, setOrders] = useState<Order[]>([]);
  const [mechanic, setMechanic] = useState<Mechanic | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mechanicData = localStorage.getItem('mechanic_data');
    if (!mechanicData) {
      navigate('/mechanic/login');
      return;
    }
    setMechanic(JSON.parse(mechanicData));
    fetchOrders();
  }, [navigate]);

  const fetchOrders = async () => {
    try {
      const response = await api.get<Order[]>('/mechanic/orders');
      setOrders(response.data);
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Ошибка загрузки заказов');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('mechanic_token');
    localStorage.removeItem('mechanic_data');
    navigate('/mechanic/login');
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

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Felix Hub - Механик</h1>
          <Button variant="outline" onClick={handleLogout}>
            Выход
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        {mechanic && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Добро пожаловать, {mechanic.name}!</CardTitle>
              <CardDescription>Ваши заказы</CardDescription>
            </CardHeader>
          </Card>
        )}

        <div className="space-y-4">
          {orders.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <p className="text-center text-muted-foreground">Нет активных заказов</p>
              </CardContent>
            </Card>
          ) : (
            orders.map((order) => (
              <Card key={order.id} className="cursor-pointer hover:bg-accent/50 transition-colors"
                onClick={() => navigate(`/mechanic/orders/${order.id}`)}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">Заказ #{order.id}</CardTitle>
                      <CardDescription>VIN: {order.vin}</CardDescription>
                    </div>
                    <Badge variant={getStatusVariant(order.status)}>
                      {order.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <p><strong>Категория:</strong> {order.category}</p>
                    <p><strong>Деталь:</strong> {order.part_name}</p>
                    <p><strong>Тип:</strong> {order.part_type}</p>
                    <p className="text-muted-foreground">
                      {format(new Date(order.created_at), 'dd MMMM yyyy, HH:mm', { locale: ru })}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </main>
    </div>
  );
}
