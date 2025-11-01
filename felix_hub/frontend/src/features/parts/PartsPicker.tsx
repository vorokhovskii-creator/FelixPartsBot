import { useEffect, useState, useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search, X } from 'lucide-react';
import { toast } from 'sonner';
import { partsApi } from '@/api/parts';
import type { Category, Part } from '@/types';

interface PartsPickerProps {
  selectedIds?: number[];
  onSelect?: (ids: number[]) => void;
  onConfirm?: (ids: number[]) => void;
  multiSelect?: boolean;
  showConfirmButton?: boolean;
  confirmButtonText?: string;
  initialCategoryId?: number;
}

export default function PartsPicker({
  selectedIds = [],
  onSelect,
  onConfirm,
  multiSelect = true,
  showConfirmButton = true,
  confirmButtonText = 'Подтвердить выбор',
  initialCategoryId,
}: PartsPickerProps) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [parts, setParts] = useState<Part[]>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(
    initialCategoryId || null
  );
  const [searchQuery, setSearchQuery] = useState('');
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [loadingParts, setLoadingParts] = useState(false);
  const [errorCategories, setErrorCategories] = useState<string | null>(null);
  const [errorParts, setErrorParts] = useState<string | null>(null);
  const [internalSelectedIds, setInternalSelectedIds] = useState<number[]>(selectedIds);

  useEffect(() => {
    setInternalSelectedIds(selectedIds);
  }, [selectedIds]);

  useEffect(() => {
    const fetchCategories = async () => {
      setLoadingCategories(true);
      setErrorCategories(null);
      try {
        const data = await partsApi.fetchCategories();
        setCategories(data);
      } catch (error) {
        const errorMessage =
          (error as { response?: { data?: { error?: string } } }).response?.data?.error ||
          'Ошибка загрузки категорий';
        setErrorCategories(errorMessage);
        toast.error(errorMessage);
      } finally {
        setLoadingCategories(false);
      }
    };

    fetchCategories();
  }, []);

  useEffect(() => {
    if (selectedCategoryId === null) {
      setParts([]);
      return;
    }

    const fetchParts = async () => {
      setLoadingParts(true);
      setErrorParts(null);
      try {
        const data = await partsApi.fetchParts(selectedCategoryId);
        setParts(data);
      } catch (error) {
        const errorMessage =
          (error as { response?: { data?: { error?: string } } }).response?.data?.error ||
          'Ошибка загрузки запчастей';
        setErrorParts(errorMessage);
        toast.error(errorMessage);
      } finally {
        setLoadingParts(false);
      }
    };

    fetchParts();
  }, [selectedCategoryId]);

  const filteredParts = useMemo(() => {
    if (!searchQuery.trim()) {
      return parts;
    }

    const query = searchQuery.toLowerCase();
    return parts.filter((part) => {
      return (
        part.name_ru?.toLowerCase().includes(query) ||
        part.name_he?.toLowerCase().includes(query) ||
        part.name_en?.toLowerCase().includes(query)
      );
    });
  }, [parts, searchQuery]);

  const handleCategorySelect = (categoryId: number) => {
    setSelectedCategoryId(categoryId);
    setSearchQuery('');
  };

  const handlePartToggle = (partId: number) => {
    let newSelection: number[];

    if (multiSelect) {
      if (internalSelectedIds.includes(partId)) {
        newSelection = internalSelectedIds.filter((id) => id !== partId);
      } else {
        newSelection = [...internalSelectedIds, partId];
      }
    } else {
      newSelection = [partId];
    }

    setInternalSelectedIds(newSelection);
    onSelect?.(newSelection);
  };

  const handleConfirm = () => {
    onConfirm?.(internalSelectedIds);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
  };

  const handleBackToCategories = () => {
    setSelectedCategoryId(null);
    setSearchQuery('');
  };

  const selectedCategory = categories.find((cat) => cat.id === selectedCategoryId);

  if (loadingCategories) {
    return (
      <div 
        className="text-center py-8" 
        role="status" 
        aria-live="polite"
        aria-label="Загрузка категорий"
      >
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
        <p className="text-gray-600">Загрузка категорий...</p>
      </div>
    );
  }

  if (errorCategories) {
    return (
      <div 
        className="text-center py-8"
        role="alert"
        aria-live="assertive"
      >
        <p className="text-red-600 mb-4">{errorCategories}</p>
        <Button onClick={() => window.location.reload()}>
          Попробовать снова
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {selectedCategoryId === null ? (
        <>
          <div>
            <h2 className="text-xl font-semibold mb-4">
              Выберите категорию
            </h2>
            <div 
              className="space-y-2"
              role="list"
              aria-label="Список категорий"
            >
              {categories.map((category) => (
                <Card
                  key={category.id}
                  className="cursor-pointer hover:bg-gray-50 transition focus-within:ring-2 focus-within:ring-blue-500"
                  onClick={() => handleCategorySelect(category.id)}
                  role="listitem"
                >
                  <CardContent className="p-4 flex items-center gap-3">
                    <button
                      className="w-full text-left flex items-center gap-3"
                      onClick={() => handleCategorySelect(category.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          handleCategorySelect(category.id);
                        }
                      }}
                      aria-label={`Выбрать категорию ${category.name_ru}`}
                    >
                      <div className="text-2xl" aria-hidden="true">
                        {category.icon}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium">{category.name_ru}</p>
                      </div>
                    </button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={handleBackToCategories}
                aria-label="Вернуться к категориям"
              >
                ← Назад
              </Button>
              <div className="flex-1">
                <h2 className="text-xl font-semibold">
                  {selectedCategory?.icon} {selectedCategory?.name_ru}
                </h2>
              </div>
            </div>

            <div className="relative">
              <label htmlFor="parts-search" className="sr-only">
                Поиск запчастей
              </label>
              <Search 
                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5"
                aria-hidden="true"
              />
              <Input
                id="parts-search"
                type="text"
                placeholder="Поиск запчастей..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-10"
                aria-label="Поиск запчастей в текущей категории"
              />
              {searchQuery && (
                <button
                  onClick={handleClearSearch}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  aria-label="Очистить поиск"
                >
                  <X className="h-5 w-5" />
                </button>
              )}
            </div>

            {loadingParts ? (
              <div 
                className="text-center py-8"
                role="status"
                aria-live="polite"
                aria-label="Загрузка запчастей"
              >
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
                <p className="text-gray-600">Загрузка запчастей...</p>
              </div>
            ) : errorParts ? (
              <div 
                className="text-center py-8"
                role="alert"
                aria-live="assertive"
              >
                <p className="text-red-600">{errorParts}</p>
              </div>
            ) : filteredParts.length === 0 ? (
              <div 
                className="text-center py-8 text-gray-500"
                role="status"
              >
                {searchQuery
                  ? 'Ничего не найдено. Попробуйте изменить запрос.'
                  : 'В этой категории пока нет запчастей.'}
              </div>
            ) : (
              <div 
                className="space-y-2"
                role="list"
                aria-label={`Список запчастей${searchQuery ? ' (результаты поиска)' : ''}`}
              >
                {filteredParts.map((part) => {
                  const isSelected = internalSelectedIds.includes(part.id);
                  return (
                    <Card
                      key={part.id}
                      className={`cursor-pointer hover:bg-gray-50 transition focus-within:ring-2 focus-within:ring-blue-500 ${
                        isSelected ? 'bg-blue-50 border-blue-500' : ''
                      }`}
                      onClick={() => handlePartToggle(part.id)}
                      role="listitem"
                    >
                      <CardContent className="p-4 flex items-center gap-3">
                        <button
                          className="w-full text-left flex items-center gap-3"
                          onClick={(e) => {
                            e.stopPropagation();
                            handlePartToggle(part.id);
                          }}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault();
                              handlePartToggle(part.id);
                            }
                          }}
                          aria-label={`${isSelected ? 'Отменить выбор' : 'Выбрать'} запчасть ${part.name_ru}`}
                          aria-pressed={isSelected}
                          role="checkbox"
                          aria-checked={isSelected}
                        >
                          <div className="text-2xl" aria-hidden="true">
                            {isSelected ? '☑️' : '☐'}
                          </div>
                          <div className="flex-1">
                            <p className="font-medium">{part.name_ru}</p>
                          </div>
                        </button>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>

          {showConfirmButton && (
            <div className="sticky bottom-0 left-0 right-0 bg-white border-t p-4 -mx-4">
              <Button
                className="w-full"
                disabled={internalSelectedIds.length === 0}
                onClick={handleConfirm}
                aria-label={`${confirmButtonText} (${internalSelectedIds.length} выбрано)`}
              >
                {confirmButtonText} ({internalSelectedIds.length} выбрано)
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
