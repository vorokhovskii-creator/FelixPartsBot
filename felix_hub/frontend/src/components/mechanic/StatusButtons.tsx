import { memo } from 'react';
import { Button } from '@/components/ui/button';
import { Play, Pause, CheckCircle } from 'lucide-react';

interface StatusButtonsProps {
  currentStatus: string;
  onStatusChange: (status: string) => void;
}

function StatusButtons({ currentStatus, onStatusChange }: StatusButtonsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
      {currentStatus === 'новый' && (
        <Button
          className="touch-target"
          onClick={() => onStatusChange('в работе')}
        >
          <Play className="h-5 w-5 mr-2" />
          Начать работу
        </Button>
      )}

      {currentStatus === 'в работе' && (
        <>
          <Button
            variant="outline"
            className="touch-target"
            onClick={() => onStatusChange('на паузе')}
          >
            <Pause className="h-5 w-5 mr-2" />
            Приостановить
          </Button>
          
          <Button
            className="touch-target bg-green-600 hover:bg-green-700"
            onClick={() => onStatusChange('завершен')}
          >
            <CheckCircle className="h-5 w-5 mr-2" />
            Завершить
          </Button>
        </>
      )}

      {currentStatus === 'на паузе' && (
        <Button
          className="touch-target"
          onClick={() => onStatusChange('в работе')}
        >
          <Play className="h-5 w-5 mr-2" />
          Продолжить
        </Button>
      )}

      {currentStatus === 'завершен' && (
        <div className="text-center text-green-600 font-medium py-3">
          ✓ Заказ завершен
        </div>
      )}
    </div>
  );
}

export default memo(StatusButtons);
