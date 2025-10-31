import { useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Camera, X, ArrowLeft } from 'lucide-react';

interface PhotoUploadProps {
  photo: string | null;
  onUpload: (photo: string | null) => void;
  onNext: () => void;
  onBack: () => void;
}

export default function PhotoUpload({ photo, onUpload, onNext, onBack }: PhotoUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        onUpload(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removePhoto = () => {
    onUpload(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h2 className="text-xl font-semibold">Фото (необязательно)</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Фото (необязательно)</CardTitle>
          <CardDescription>
            Прикрепите фото детали или повреждения
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!photo ? (
            <div>
              <input
                type="file"
                accept="image/*"
                capture="environment"
                className="hidden"
                ref={fileInputRef}
                onChange={handleFileSelect}
              />
              
              <Button
                variant="outline"
                className="w-full h-32 border-dashed"
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="flex flex-col items-center">
                  <Camera className="h-12 w-12 mb-2 text-gray-400" />
                  <span>Загрузить фото</span>
                </div>
              </Button>
            </div>
          ) : (
            <div className="relative">
              <img 
                src={photo} 
                alt="Preview" 
                className="w-full rounded-lg"
              />
              <Button
                variant="destructive"
                size="icon"
                className="absolute top-2 right-2"
                onClick={removePhoto}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}

          <Button className="w-full" onClick={onNext}>
            {photo ? 'Продолжить' : 'Пропустить'}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
