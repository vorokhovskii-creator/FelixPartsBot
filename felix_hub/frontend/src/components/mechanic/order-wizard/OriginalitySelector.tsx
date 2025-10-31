import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

interface OriginalitySelectorProps {
  selected: 'original' | 'analog' | 'any';
  onSelect: (type: 'original' | 'analog' | 'any') => void;
  onBack: () => void;
}

export default function OriginalitySelector({ selected, onSelect, onBack }: OriginalitySelectorProps) {
  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h2 className="text-xl font-semibold">Тип запчастей</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Тип запчастей</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button
            variant={selected === 'original' ? 'default' : 'outline'}
            className="w-full h-20 text-lg"
            onClick={() => onSelect('original')}
          >
            <div className="flex flex-col items-center">
              <span className="text-2xl mb-1">✅</span>
              <span>Оригинал</span>
            </div>
          </Button>

          <Button
            variant={selected === 'analog' ? 'default' : 'outline'}
            className="w-full h-20 text-lg"
            onClick={() => onSelect('analog')}
          >
            <div className="flex flex-col items-center">
              <span className="text-2xl mb-1">🔄</span>
              <span>Аналог</span>
            </div>
          </Button>

          <Button
            variant={selected === 'any' ? 'default' : 'outline'}
            className="w-full h-20 text-lg"
            onClick={() => onSelect('any')}
          >
            <div className="flex flex-col items-center">
              <span className="text-2xl mb-1">🤷</span>
              <span>Любой</span>
            </div>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
