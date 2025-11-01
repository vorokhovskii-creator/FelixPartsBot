import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ArrowLeft } from 'lucide-react';

interface VinInputProps {
  value: string;
  onChange: (value: string) => void;
  onNext: () => void;
  onBack: () => void;
}

export default function VinInput({ value, onChange, onNext, onBack }: VinInputProps) {
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (value.trim().length === 0) {
      setError('Номер автомобиля обязателен');
      return;
    }
    
    if (value.length < 4) {
      setError('Номер автомобиля должен содержать минимум 4 символа');
      return;
    }
    
    if (value.length > 20) {
      setError('Номер автомобиля не может превышать 20 символов');
      return;
    }
    
    setError('');
    onNext();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value.toUpperCase();
    onChange(newValue);
    if (error) {
      setError('');
    }
  };

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h2 className="text-xl font-semibold">Номер автомобиля</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Номер автомобиля</CardTitle>
          <CardDescription>
            Введите госномер или VIN автомобиля
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <Label htmlFor="carNumber">Номер автомобиля</Label>
                <Input
                  id="carNumber"
                  placeholder="12-345-67 или WBADT43452G123456"
                  value={value}
                  onChange={handleChange}
                  maxLength={20}
                  className="font-mono text-lg"
                />
                {value && (
                  <p className="text-sm text-gray-500 mt-1">
                    {value.length} символов
                  </p>
                )}
                {error && (
                  <p className="text-sm text-red-500 mt-1">{error}</p>
                )}
              </div>

              <Button type="submit" className="w-full">
                Продолжить
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
