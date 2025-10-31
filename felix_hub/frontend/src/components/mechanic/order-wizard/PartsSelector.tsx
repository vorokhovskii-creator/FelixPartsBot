import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';
import type { Part } from '@/types';

interface PartsSelectorProps {
  categoryId: number;
  selectedIds: number[];
  onSelect: (ids: number[]) => void;
  onNext: () => void;
  onBack: () => void;
}

export default function PartsSelector({
  categoryId,
  selectedIds,
  onSelect,
  onNext,
  onBack,
}: PartsSelectorProps) {
  const [parts, setParts] = useState<Part[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchParts = async () => {
      setLoading(true);
      try {
        const response = await api.get('/parts', {
          params: { category_id: categoryId },
        });
        setParts(response.data);
      } catch (error: any) {
        toast.error(error.response?.data?.error || 'Ошибка загрузки запчастей');
      } finally {
        setLoading(false);
      }
    };

    if (categoryId) {
      fetchParts();
    }
  }, [categoryId]);

  const togglePart = (partId: number) => {
    if (selectedIds.includes(partId)) {
      onSelect(selectedIds.filter((id) => id !== partId));
    } else {
      onSelect([...selectedIds, partId]);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Загрузка запчастей...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h2 className="text-xl font-semibold">Выберите запчасти</h2>
      </div>

      <div className="space-y-2 pb-20">
        {parts.map((part) => (
          <Card
            key={part.id}
            className={`cursor-pointer hover:bg-gray-50 transition ${
              selectedIds.includes(part.id) ? 'bg-blue-50 border-blue-500' : ''
            }`}
            onClick={() => togglePart(part.id)}
          >
            <CardContent className="p-4 flex items-center gap-3">
              <div className="text-2xl">
                {selectedIds.includes(part.id) ? '☑️' : '☐'}
              </div>
              <div className="flex-1">
                <p className="font-medium">{part.name_ru}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4">
        <div className="container max-w-2xl mx-auto">
          <Button
            className="w-full"
            disabled={selectedIds.length === 0}
            onClick={onNext}
          >
            Продолжить ({selectedIds.length} выбрано)
          </Button>
        </div>
      </div>
    </div>
  );
}
