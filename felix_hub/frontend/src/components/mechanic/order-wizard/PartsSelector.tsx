import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ArrowLeft, Plus, Edit, Trash2, Package } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';
import type { Part, SelectedPart } from '@/types';

interface PartsSelectorProps {
  categoryId: number;
  selectedParts: SelectedPart[];
  onSelectParts: (parts: SelectedPart[]) => void;
  onNext: () => void;
  onBack: () => void;
}

export default function PartsSelector({
  categoryId,
  selectedParts,
  onSelectParts,
  onNext,
  onBack,
}: PartsSelectorProps) {
  const [parts, setParts] = useState<Part[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCustomForm, setShowCustomForm] = useState(false);
  const [customPartName, setCustomPartName] = useState('');
  const [customPartQuantity, setCustomPartQuantity] = useState('1');
  const [customPartPrice, setCustomPartPrice] = useState('');
  const [editingCustomIndex, setEditingCustomIndex] = useState<number | null>(null);

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

  const togglePart = (part: Part) => {
    const existingIndex = selectedParts.findIndex((p) => !p.isCustom && p.id === part.id);
    if (existingIndex >= 0) {
      onSelectParts(selectedParts.filter((_, idx) => idx !== existingIndex));
    } else {
      onSelectParts([...selectedParts, { id: part.id, name: part.name_ru, isCustom: false }]);
    }
  };

  const isPartSelected = (partId: number) => {
    return selectedParts.some((p) => !p.isCustom && p.id === partId);
  };

  const handleAddCustomPart = () => {
    if (!customPartName.trim()) {
      toast.error('Название запчасти обязательно');
      return;
    }

    const quantity = parseInt(customPartQuantity);
    if (isNaN(quantity) || quantity <= 0) {
      toast.error('Количество должно быть больше 0');
      return;
    }

    const price = customPartPrice ? parseFloat(customPartPrice) : undefined;
    if (customPartPrice && (isNaN(price!) || price! < 0)) {
      toast.error('Некорректная цена');
      return;
    }

    const newCustomPart: SelectedPart = {
      name: customPartName.trim(),
      quantity,
      price,
      isCustom: true,
    };

    if (editingCustomIndex !== null) {
      const updated = [...selectedParts];
      updated[editingCustomIndex] = newCustomPart;
      onSelectParts(updated);
      toast.success('Запчасть обновлена');
    } else {
      onSelectParts([...selectedParts, newCustomPart]);
      toast.success('Кастомная запчасть добавлена');
    }

    setCustomPartName('');
    setCustomPartQuantity('1');
    setCustomPartPrice('');
    setShowCustomForm(false);
    setEditingCustomIndex(null);
  };

  const handleEditCustomPart = (index: number) => {
    const part = selectedParts[index];
    if (part.isCustom) {
      setCustomPartName(part.name);
      setCustomPartQuantity(part.quantity?.toString() || '1');
      setCustomPartPrice(part.price?.toString() || '');
      setEditingCustomIndex(index);
      setShowCustomForm(true);
    }
  };

  const handleRemoveCustomPart = (index: number) => {
    onSelectParts(selectedParts.filter((_, idx) => idx !== index));
    toast.success('Запчасть удалена');
  };

  const handleCancelCustomForm = () => {
    setCustomPartName('');
    setCustomPartQuantity('1');
    setCustomPartPrice('');
    setShowCustomForm(false);
    setEditingCustomIndex(null);
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Загрузка запчастей...</p>
      </div>
    );
  }

  const customParts = selectedParts.filter((p) => p.isCustom);
  const catalogParts = selectedParts.filter((p) => !p.isCustom);

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h2 className="text-xl font-semibold">Выберите запчасти</h2>
      </div>

      <div className="space-y-2 pb-32">
        {parts.map((part) => (
          <Card
            key={part.id}
            className={`cursor-pointer hover:bg-gray-50 transition ${
              isPartSelected(part.id) ? 'bg-blue-50 border-blue-500' : ''
            }`}
            onClick={() => togglePart(part)}
          >
            <CardContent className="p-4 flex items-center gap-3">
              <div className="text-2xl">
                {isPartSelected(part.id) ? '☑️' : '☐'}
              </div>
              <div className="flex-1">
                <p className="font-medium">{part.name_ru}</p>
              </div>
            </CardContent>
          </Card>
        ))}

        {customParts.map((part, idx) => {
          const actualIndex = selectedParts.findIndex((p) => p === part);
          return (
            <Card key={`custom-${idx}`} className="bg-amber-50 border-amber-500">
              <CardContent className="p-4 flex items-center gap-3">
                <div className="text-2xl">
                  <Package className="h-6 w-6 text-amber-600" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-medium">{part.name}</p>
                    <span className="text-xs bg-amber-200 text-amber-800 px-2 py-0.5 rounded">Кастомная</span>
                  </div>
                  <p className="text-sm text-gray-600">
                    Кол-во: {part.quantity || 1}
                    {part.price && ` • Цена: ${part.price} ₪`}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditCustomPart(actualIndex);
                    }}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveCustomPart(actualIndex);
                    }}
                  >
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}

        {!showCustomForm && (
          <Card
            className="cursor-pointer hover:bg-gray-50 transition border-dashed border-2"
            onClick={() => setShowCustomForm(true)}
          >
            <CardContent className="p-4 flex items-center gap-3">
              <div className="text-2xl">
                <Plus className="h-6 w-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="font-medium text-blue-600">Добавить кастомную запчасть</p>
              </div>
            </CardContent>
          </Card>
        )}

        {showCustomForm && (
          <Card className="border-blue-500">
            <CardContent className="p-4 space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Название запчасти <span className="text-red-500">*</span>
                </label>
                <Input
                  value={customPartName}
                  onChange={(e) => setCustomPartName(e.target.value)}
                  placeholder="Введите название запчасти"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Количество <span className="text-red-500">*</span>
                  </label>
                  <Input
                    type="number"
                    min="1"
                    value={customPartQuantity}
                    onChange={(e) => setCustomPartQuantity(e.target.value)}
                    placeholder="1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Цена (₪)</label>
                  <Input
                    type="number"
                    min="0"
                    step="0.01"
                    value={customPartPrice}
                    onChange={(e) => setCustomPartPrice(e.target.value)}
                    placeholder="Опционально"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={handleCancelCustomForm}
                >
                  Отмена
                </Button>
                <Button className="flex-1" onClick={handleAddCustomPart}>
                  {editingCustomIndex !== null ? 'Сохранить' : 'Добавить'}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4">
        <div className="container max-w-2xl mx-auto">
          <Button
            className="w-full"
            disabled={selectedParts.length === 0}
            onClick={onNext}
          >
            Продолжить ({selectedParts.length} выбрано)
          </Button>
        </div>
      </div>
    </div>
  );
}
