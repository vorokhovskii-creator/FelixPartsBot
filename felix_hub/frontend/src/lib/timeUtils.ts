import { format, startOfDay, endOfDay, subDays, startOfWeek, startOfMonth } from 'date-fns';
import { ru } from 'date-fns/locale';
import type { TimeLog, GroupedTimeLog } from '@/types';

/**
 * Format duration in minutes to human readable format
 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}м`;
  }
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}ч ${mins}м` : `${hours}ч`;
}

/**
 * Format duration in minutes to hours format
 */
export function formatHours(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours === 0) {
    return `${mins}м`;
  }
  return `${hours}ч${mins > 0 ? ` ${mins}м` : ''}`;
}

/**
 * Format time from ISO string to HH:mm
 */
export function formatTime(dateString: string): string {
  return format(new Date(dateString), 'HH:mm', { locale: ru });
}

/**
 * Format date from ISO string or date string to readable format
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const today = startOfDay(new Date());
  const yesterday = startOfDay(subDays(new Date(), 1));
  const dateStart = startOfDay(date);

  if (dateStart.getTime() === today.getTime()) {
    return 'Сегодня';
  } else if (dateStart.getTime() === yesterday.getTime()) {
    return 'Вчера';
  } else {
    return format(date, 'd MMMM yyyy', { locale: ru });
  }
}

/**
 * Group time logs by day
 */
export function groupByDay(sessions: TimeLog[]): GroupedTimeLog[] {
  const grouped = new Map<string, TimeLog[]>();

  sessions.forEach((session) => {
    const dateKey = format(new Date(session.started_at), 'yyyy-MM-dd');
    if (!grouped.has(dateKey)) {
      grouped.set(dateKey, []);
    }
    grouped.get(dateKey)!.push(session);
  });

  const result: GroupedTimeLog[] = [];
  grouped.forEach((sessions, date) => {
    const total_minutes = sessions.reduce(
      (sum, session) => sum + (session.duration_minutes || 0),
      0
    );
    result.push({
      date,
      sessions,
      total_minutes,
    });
  });

  // Sort by date descending
  result.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  return result;
}

/**
 * Get date range for a period
 */
export function getDateRange(period: 'today' | 'yesterday' | 'week' | 'month' | 'custom'): {
  start_date: string;
  end_date: string;
} {
  const now = new Date();
  let startDate: Date;
  let endDate: Date = endOfDay(now);

  switch (period) {
    case 'today':
      startDate = startOfDay(now);
      break;
    case 'yesterday':
      const yesterday = subDays(now, 1);
      startDate = startOfDay(yesterday);
      endDate = endOfDay(yesterday);
      break;
    case 'week':
      startDate = startOfWeek(now, { locale: ru });
      break;
    case 'month':
      startDate = startOfMonth(now);
      break;
    default:
      startDate = startOfDay(now);
  }

  return {
    start_date: format(startDate, 'yyyy-MM-dd'),
    end_date: format(endDate, 'yyyy-MM-dd'),
  };
}
