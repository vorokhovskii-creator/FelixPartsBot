import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Clock, Play, TrendingUp, Package, ExternalLink } from 'lucide-react';
import api from '@/lib/api';
import { formatDuration, formatHours, formatTime, formatDate, groupByDay, getDateRange } from '@/lib/timeUtils';
import type { TimeHistoryStats, GroupedTimeLog } from '@/types';

type Period = 'today' | 'yesterday' | 'week' | 'month' | 'custom';

export default function MechanicTimeHistory() {
  const [stats, setStats] = useState<TimeHistoryStats>({
    total_minutes: 0,
    sessions_count: 0,
    orders_count: 0,
    avg_session: 0
  });
  const [groupedSessions, setGroupedSessions] = useState<GroupedTimeLog[]>([]);
  const [period, setPeriod] = useState<Period>('today');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchTimeHistory = useCallback(async (customStart?: string, customEnd?: string) => {
    setLoading(true);
    try {
      let params: { start_date: string; end_date: string };

      if (customStart && customEnd) {
        params = { start_date: customStart, end_date: customEnd };
      } else {
        params = getDateRange(period);
      }

      const response = await api.get('/mechanic/time/history', { params });
      setStats(response.data.stats);
      setGroupedSessions(groupByDay(response.data.sessions));
    } catch (error) {
      console.error('Error fetching time history:', error);
    } finally {
      setLoading(false);
    }
  }, [period]);

  useEffect(() => {
    if (period !== 'custom') {
      fetchTimeHistory();
    }
  }, [period, fetchTimeHistory]);

  const applyCustomPeriod = () => {
    if (startDate && endDate) {
      fetchTimeHistory(startDate, endDate);
    }
  };

  return (
    <div className="container max-w-4xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-6">История рабочего времени</h1>

      {/* Статистика */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <Card>
          <CardContent className="p-4 text-center">
            <Clock className="h-8 w-8 mx-auto mb-2 text-blue-600" />
            <p className="text-2xl font-bold">{formatHours(stats.total_minutes)}</p>
            <p className="text-xs text-gray-600">Всего времени</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Play className="h-8 w-8 mx-auto mb-2 text-green-600" />
            <p className="text-2xl font-bold">{stats.sessions_count}</p>
            <p className="text-xs text-gray-600">Сессий</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <TrendingUp className="h-8 w-8 mx-auto mb-2 text-orange-600" />
            <p className="text-2xl font-bold">{formatDuration(Math.round(stats.avg_session))}</p>
            <p className="text-xs text-gray-600">Средняя сессия</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Package className="h-8 w-8 mx-auto mb-2 text-purple-600" />
            <p className="text-2xl font-bold">{stats.orders_count}</p>
            <p className="text-xs text-gray-600">Заказов</p>
          </CardContent>
        </Card>
      </div>

      {/* Фильтры периода */}
      <Tabs value={period} onValueChange={(value) => setPeriod(value as Period)} className="mb-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="today">Сегодня</TabsTrigger>
          <TabsTrigger value="yesterday">Вчера</TabsTrigger>
          <TabsTrigger value="week">Неделя</TabsTrigger>
          <TabsTrigger value="month">Месяц</TabsTrigger>
          <TabsTrigger value="custom">Выбрать</TabsTrigger>
        </TabsList>
      </Tabs>

      {period === 'custom' && (
        <div className="flex gap-2 mb-6">
          <Input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            placeholder="Дата начала"
          />
          <Input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            placeholder="Дата окончания"
          />
          <Button onClick={applyCustomPeriod}>Применить</Button>
        </div>
      )}

      {/* Список сессий */}
      <div className="space-y-6">
        {loading ? (
          <div className="text-center py-8 text-gray-500">Загрузка...</div>
        ) : groupedSessions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Нет записей за выбранный период
          </div>
        ) : (
          groupedSessions.map(day => (
            <Card key={day.date}>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle className="text-lg">
                    {formatDate(day.date)}
                  </CardTitle>
                  <Badge variant="secondary">
                    {formatDuration(day.total_minutes)}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {day.sessions.map(session => (
                    <div
                      key={session.id}
                      className="border-l-4 border-blue-500 pl-4 py-2 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium">
                            {formatTime(session.started_at)} -{' '}
                            {session.ended_at ? formatTime(session.ended_at) : 'в процессе'}
                          </p>
                          <p className="text-sm text-gray-600">
                            Заказ #{session.order_id} ({session.duration_minutes || 0} мин)
                          </p>
                          {session.notes && (
                            <p className="text-sm text-gray-500 mt-1">{session.notes}</p>
                          )}
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/mechanic/orders/${session.order_id}`);
                          }}
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
