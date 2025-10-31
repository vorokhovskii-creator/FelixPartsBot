import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { TimeLog } from '@/types';

interface TimeTrackerProps {
  orderId: number;
  timeLogs: TimeLog[];
}

export default function TimeTracker({ orderId, timeLogs }: TimeTrackerProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Учет времени</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">
          Функция учета времени будет реализована в следующей задаче
        </p>
        {timeLogs.length > 0 && (
          <div className="mt-4 space-y-2">
            {timeLogs.map((log) => (
              <div key={log.id} className="text-sm">
                <p>Запись #{log.id}</p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
