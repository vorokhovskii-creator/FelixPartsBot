import { useParams, useNavigate } from 'react-router-dom';
import OrderDetails from '@/features/orders/OrderDetails';

export default function OrderDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  if (!id) {
    return <div className="p-4">Заказ не найден</div>;
  }

  return (
    <OrderDetails
      orderId={id}
      onBack={() => navigate('/mechanic/dashboard')}
    />
  );
}
