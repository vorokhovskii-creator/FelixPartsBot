import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface CustomItemsSectionProps {
  orderId: number;
  onItemAdded: () => void;
}

export default function CustomItemsSection({ orderId, onItemAdded }: CustomItemsSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Дополнительные позиции</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">
          Функция добавления кастомных позиций будет реализована в следующей задаче
        </p>
      </CardContent>
    </Card>
  );
}
