import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import api from '@/lib/api';

interface CustomItemsSectionProps {
  orderId: number;
  onItemAdded: () => void;
}

const customWorkSchema = z.object({
  name: z.string().min(1, 'Укажите название работы'),
  description: z.string().optional(),
  price: z.string().min(1, 'Укажите цену').refine(
    (val) => {
      const num = parseFloat(val);
      return !isNaN(num) && num > 0;
    },
    { message: 'Цена должна быть больше 0' }
  ),
  estimated_time_minutes: z.string().optional().refine(
    (val) => {
      if (!val || val.trim() === '') return true;
      const num = parseInt(val);
      return !isNaN(num) && num > 0;
    },
    { message: 'Время должно быть положительным числом' }
  ),
});

const customPartSchema = z.object({
  name: z.string().min(1, 'Укажите название запчасти'),
  part_number: z.string().optional(),
  price: z.string().min(1, 'Укажите цену').refine(
    (val) => {
      const num = parseFloat(val);
      return !isNaN(num) && num > 0;
    },
    { message: 'Цена должна быть больше 0' }
  ),
  quantity: z.string().min(1, 'Укажите количество').refine(
    (val) => {
      const num = parseInt(val);
      return !isNaN(num) && num > 0;
    },
    { message: 'Количество должно быть больше 0' }
  ),
});

type CustomWorkForm = z.infer<typeof customWorkSchema>;
type CustomPartForm = z.infer<typeof customPartSchema>;

export default function CustomItemsSection({ orderId, onItemAdded }: CustomItemsSectionProps) {
  const [activeTab, setActiveTab] = useState('works');

  const {
    register: registerWork,
    handleSubmit: handleSubmitWork,
    reset: resetWork,
    formState: { errors: errorsWork, isSubmitting: isSubmittingWork },
  } = useForm<CustomWorkForm>({
    resolver: zodResolver(customWorkSchema),
  });

  const {
    register: registerPart,
    handleSubmit: handleSubmitPart,
    reset: resetPart,
    formState: { errors: errorsPart, isSubmitting: isSubmittingPart },
  } = useForm<CustomPartForm>({
    resolver: zodResolver(customPartSchema),
    defaultValues: {
      quantity: '1',
    },
  });

  const onSubmitWork = async (data: CustomWorkForm) => {
    try {
      const payload = {
        name: data.name,
        description: data.description || '',
        price: parseFloat(data.price),
        estimated_time_minutes: data.estimated_time_minutes 
          ? parseInt(data.estimated_time_minutes) 
          : 0,
      };
      await api.post(`/mechanic/orders/${orderId}/custom-works`, payload);
      toast.success('Работа добавлена');
      resetWork();
      onItemAdded();
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Ошибка добавления работы');
    }
  };

  const onSubmitPart = async (data: CustomPartForm) => {
    try {
      const payload = {
        name: data.name,
        part_number: data.part_number || '',
        price: parseFloat(data.price),
        quantity: parseInt(data.quantity),
      };
      await api.post(`/mechanic/orders/${orderId}/custom-parts`, payload);
      toast.success('Запчасть добавлена');
      resetPart({ quantity: '1' });
      onItemAdded();
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Ошибка добавления запчасти');
    }
  };

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab}>
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="works">Работы</TabsTrigger>
        <TabsTrigger value="parts">Запчасти</TabsTrigger>
      </TabsList>

      <TabsContent value="works">
        <Card>
          <CardHeader>
            <CardTitle>Добавить кастомную работу</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmitWork(onSubmitWork)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="work_name">Название работы *</Label>
                <Input
                  id="work_name"
                  placeholder="Например: Замена масла"
                  {...registerWork('name')}
                />
                {errorsWork.name && (
                  <p className="text-sm text-destructive">{errorsWork.name.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="work_description">Описание</Label>
                <Textarea
                  id="work_description"
                  placeholder="Дополнительная информация о работе (опционально)"
                  {...registerWork('description')}
                  rows={3}
                />
                {errorsWork.description && (
                  <p className="text-sm text-destructive">{errorsWork.description.message}</p>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="work_price">Цена (₪) *</Label>
                  <Input
                    id="work_price"
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    {...registerWork('price')}
                  />
                  {errorsWork.price && (
                    <p className="text-sm text-destructive">{errorsWork.price.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="work_time">Время (мин)</Label>
                  <Input
                    id="work_time"
                    type="number"
                    placeholder="Опционально"
                    {...registerWork('estimated_time_minutes')}
                  />
                  {errorsWork.estimated_time_minutes && (
                    <p className="text-sm text-destructive">
                      {errorsWork.estimated_time_minutes.message}
                    </p>
                  )}
                </div>
              </div>

              <Button
                type="submit"
                disabled={isSubmittingWork}
                className="w-full min-h-[44px]"
              >
                Добавить работу
              </Button>
            </form>
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="parts">
        <Card>
          <CardHeader>
            <CardTitle>Добавить кастомную запчасть</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmitPart(onSubmitPart)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="part_name">Название запчасти *</Label>
                <Input
                  id="part_name"
                  placeholder="Например: Масляный фильтр"
                  {...registerPart('name')}
                />
                {errorsPart.name && (
                  <p className="text-sm text-destructive">{errorsPart.name.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="part_number">Артикул</Label>
                <Input
                  id="part_number"
                  placeholder="Артикул или номер детали (опционально)"
                  {...registerPart('part_number')}
                />
                {errorsPart.part_number && (
                  <p className="text-sm text-destructive">{errorsPart.part_number.message}</p>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="part_price">Цена (₪) *</Label>
                  <Input
                    id="part_price"
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    {...registerPart('price')}
                  />
                  {errorsPart.price && (
                    <p className="text-sm text-destructive">{errorsPart.price.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="part_quantity">Количество *</Label>
                  <Input
                    id="part_quantity"
                    type="number"
                    min="1"
                    {...registerPart('quantity')}
                  />
                  {errorsPart.quantity && (
                    <p className="text-sm text-destructive">{errorsPart.quantity.message}</p>
                  )}
                </div>
              </div>

              <Button
                type="submit"
                disabled={isSubmittingPart}
                className="w-full min-h-[44px]"
              >
                Добавить запчасть
              </Button>
            </form>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}
