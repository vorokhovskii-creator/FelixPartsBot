import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';
import type { Category, Part } from '@/types';

interface OrderConfirmationProps {
  categoryId: number;
  partIds: number[];
  carNumber: string;
  partType: 'original' | 'analog' | 'any';
  photo: string | null;
  onSubmit: () => void;
  onBack: () => void;
}

export default function OrderConfirmation({
  categoryId,
  partIds,
  carNumber,
  partType,
  photo,
  onSubmit,
  onBack,
}: OrderConfirmationProps) {
  const [category, setCategory] = useState<Category | null>(null);
  const [parts, setParts] = useState<Part[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [categoryRes, partsRes] = await Promise.all([
          api.get(`/categories`),
          api.get(`/parts`, { params: { category_id: categoryId } }),
        ]);

        const foundCategory = categoryRes.data.find((c: Category) => c.id === categoryId);
        setCategory(foundCategory || null);

        const selectedParts = partsRes.data.filter((p: Part) => partIds.includes(p.id));
        setParts(selectedParts);
      } catch (error: any) {
        toast.error(error.response?.data?.error || 'Ошибка загрузки данных');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [categoryId, partIds]);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await onSubmit();
    } finally {
      setIsSubmitting(false);
    }
  };

  const getPartTypeLabel = (type: 'original' | 'analog' | 'any') => {
    const labels = {
      original: 'Оригинал',
      analog: 'Аналог',
      any: 'Любой',
    };
    return labels[type];
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Загрузка...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h2 className="text-xl font-semibold">Подтверждение заказа</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Подтверждение заказа</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">Категория:</h3>
            <p>{category?.name_ru}</p>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Запчасти:</h3>
            <ul className="space-y-1">
              {parts.map((part) => (
                <li key={part.id} className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" />
                  <span>{part.name_ru}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-1">Номер автомобиля:</h3>
            <p className="font-mono text-lg">{carNumber}</p>
          </div>

          <div>
            <h3 className="font-semibold mb-1">Тип запчастей:</h3>
            <Badge>{getPartTypeLabel(partType)}</Badge>
          </div>

          {photo && (
            <div>
              <h3 className="font-semibold mb-2">Фото:</h3>
              <img src={photo} alt="Order" className="w-32 h-32 object-cover rounded" />
            </div>
          )}

          <div className="flex gap-2 pt-4">
            <Button 
              variant="outline" 
              className="flex-1"
              onClick={onBack}
              disabled={isSubmitting}
            >
              Назад
            </Button>
            <Button 
              className="flex-1"
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Отправка...' : 'Подтвердить заказ'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
