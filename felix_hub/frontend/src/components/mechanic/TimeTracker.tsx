import { useState, useEffect } from 'react';
import { Clock, Play, Square, Plus } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { toast } from 'sonner';
import api from '@/lib/api';
import type { TimeLog } from '@/types';

interface TimeTrackerProps {
  orderId: number;
  timeLogs: TimeLog[];
}

const manualTimeSchema = z.object({
  started_at: z.string().min(1, 'Укажите дату начала'),
  ended_at: z.string().min(1, 'Укажите дату окончания'),
  notes: z.string().optional(),
});

type ManualTimeForm = z.infer<typeof manualTimeSchema>;

export default function TimeTracker({ orderId, timeLogs }: TimeTrackerProps) {
  const [activeTimer, setActiveTimer] = useState<TimeLog | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [loading, setLoading] = useState(false);
  const [showManualForm, setShowManualForm] = useState(false);
  const [notes, setNotes] = useState('');
  const [logs, setLogs] = useState<TimeLog[]>(timeLogs);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ManualTimeForm>({
    resolver: zodResolver(manualTimeSchema),
  });

  useEffect(() => {
    fetchActiveTimer();
  }, []);

  useEffect(() => {
    setLogs(timeLogs);
  }, [timeLogs]);

  useEffect(() => {
    if (!activeTimer) return;

    const interval = setInterval(() => {
      const start = new Date(activeTimer.started_at).getTime();
      const now = Date.now();
      setElapsed(Math.floor((now - start) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [activeTimer]);

  const fetchActiveTimer = async () => {
    try {
      const response = await api.get('/mechanic/time/active');
      if (response.data && response.data.order_id === orderId) {
        setActiveTimer(response.data);
        const start = new Date(response.data.started_at).getTime();
        const now = Date.now();
        setElapsed(Math.floor((now - start) / 1000));
      }
    } catch (error) {
      // No active timer
    }
  };

  const startTimer = async () => {
    setLoading(true);
    try {
      const response = await api.post(`/mechanic/orders/${orderId}/time/start`);
      setActiveTimer(response.data);
      setElapsed(0);
      toast.success('Таймер запущен');
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Ошибка запуска таймера');
    } finally {
      setLoading(false);
    }
  };

  const stopTimer = async () => {
    setLoading(true);
    try {
      await api.post(`/mechanic/orders/${orderId}/time/stop`, {
        notes: notes.trim() || undefined,
      });
      setActiveTimer(null);
      setElapsed(0);
      setNotes('');
      toast.success('Время сохранено');
      window.location.reload();
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Ошибка остановки таймера');
    } finally {
      setLoading(false);
    }
  };

  const onSubmitManualTime = async (data: ManualTimeForm) => {
    try {
      await api.post(`/mechanic/orders/${orderId}/time/manual`, data);
      toast.success('Время добавлено');
      reset();
      setShowManualForm(false);
      window.location.reload();
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Ошибка добавления времени');
    }
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}ч ${minutes}м ${secs}с`;
    }
    if (minutes > 0) {
      return `${minutes}м ${secs}с`;
    }
    return `${secs}с`;
  };

  const formatTimeRange = (start: string, end: string | null) => {
    if (!end) return format(new Date(start), 'dd MMM yyyy, HH:mm', { locale: ru });
    return `${format(new Date(start), 'dd MMM yyyy, HH:mm', { locale: ru })} - ${format(new Date(end), 'HH:mm', { locale: ru })}`;
  };

  const formatDurationMinutes = (minutes: number | null) => {
    if (!minutes) return '';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `(${hours}ч ${mins}м)`;
    }
    return `(${mins}м)`;
  };

  return (
    <div className="space-y-4">
      {/* Active Timer Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Текущая работа
          </CardTitle>
        </CardHeader>
        <CardContent>
          {activeTimer ? (
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-4xl font-bold text-primary">
                  {formatDuration(elapsed)}
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  Работа начата: {format(new Date(activeTimer.started_at), 'dd MMM yyyy, HH:mm', { locale: ru })}
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Заметки (опционально)</Label>
                <Textarea
                  id="notes"
                  placeholder="Добавьте заметки о выполненной работе..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                />
              </div>

              <Button
                onClick={stopTimer}
                disabled={loading}
                className="w-full min-h-[44px]"
                variant="destructive"
              >
                <Square className="mr-2 h-4 w-4" />
                Остановить
              </Button>
            </div>
          ) : (
            <Button
              onClick={startTimer}
              disabled={loading}
              className="w-full min-h-[44px]"
            >
              <Play className="mr-2 h-4 w-4" />
              Начать работу
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Time History Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>История времени</CardTitle>
            <Button
              onClick={() => setShowManualForm(true)}
              variant="outline"
              size="sm"
            >
              <Plus className="mr-1 h-4 w-4" />
              Добавить вручную
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {logs.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              История времени пока пуста
            </p>
          ) : (
            <div className="space-y-3">
              {[...logs]
                .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())
                .map((log) => (
                  <div key={log.id} className="border-b pb-3 last:border-0">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="text-sm font-medium">
                          {formatTimeRange(log.started_at, log.ended_at)}
                        </p>
                        {log.notes && (
                          <p className="text-sm text-muted-foreground mt-1">
                            {log.notes}
                          </p>
                        )}
                      </div>
                      {log.duration_minutes && (
                        <span className="text-sm font-semibold text-primary ml-2">
                          {formatDurationMinutes(log.duration_minutes)}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Manual Time Entry Dialog */}
      <Dialog open={showManualForm} onOpenChange={setShowManualForm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Добавить время вручную</DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit(onSubmitManualTime)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="started_at">Дата и время начала</Label>
              <Input
                id="started_at"
                type="datetime-local"
                {...register('started_at')}
              />
              {errors.started_at && (
                <p className="text-sm text-destructive">{errors.started_at.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="ended_at">Дата и время окончания</Label>
              <Input
                id="ended_at"
                type="datetime-local"
                {...register('ended_at')}
              />
              {errors.ended_at && (
                <p className="text-sm text-destructive">{errors.ended_at.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="manual_notes">Заметки</Label>
              <Textarea
                id="manual_notes"
                placeholder="Описание выполненной работы..."
                {...register('notes')}
                rows={3}
              />
            </div>

            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowManualForm(false);
                  reset();
                }}
                className="flex-1"
              >
                Отмена
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting}
                className="flex-1"
              >
                Добавить
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
