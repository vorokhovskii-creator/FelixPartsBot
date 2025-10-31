import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';
import api from '@/lib/api';
import type { Category } from '@/types';

interface CategorySelectorProps {
  selected: number | null;
  onSelect: (id: number) => void;
}

export default function CategorySelector({ selected, onSelect }: CategorySelectorProps) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await api.get('/categories');
        setCategories(response.data);
      } catch (error: any) {
        toast.error(error.response?.data?.error || 'Ошибка загрузки категорий');
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Загрузка категорий...</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Выберите категорию</h2>
      <div className="grid grid-cols-2 gap-3">
        {categories.map((category) => (
          <Card
            key={category.id}
            className={`cursor-pointer hover:shadow-lg transition ${
              selected === category.id ? 'ring-2 ring-blue-500' : ''
            }`}
            onClick={() => onSelect(category.id)}
          >
            <CardContent className="p-4 text-center">
              <div className="text-3xl mb-2">{category.icon}</div>
              <p className="font-medium">{category.name_ru}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
