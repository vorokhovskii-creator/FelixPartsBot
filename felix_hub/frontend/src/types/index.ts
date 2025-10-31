export interface Order {
  id: number;
  mechanic_name: string;
  vin: string;
  category: string;
  part_name: string;
  part_type: string;
  status: 'новый' | 'в работе' | 'готов' | 'выдан';
  work_status: 'новый' | 'в работе' | 'на паузе' | 'завершен';
  photo_url?: string;
  phone?: string;
  created_at: string;
  updated_at: string;
  total_time_minutes: number;
  comments_count: number;
}

export interface Comment {
  id: number;
  comment: string;
  created_at: string;
  mechanic_name: string;
}

export interface TimeLog {
  id: number;
  order_id: number;
  mechanic_id: number;
  started_at: string;
  ended_at: string | null;
  duration_minutes: number | null;
  notes: string;
  is_active: boolean;
}

export interface CustomWork {
  id: number;
  name: string;
  description: string;
  price: number;
  estimated_time_minutes: number;
}

export interface CustomPart {
  id: number;
  name: string;
  part_number: string;
  price: number;
  quantity: number;
}

export interface OrderDetails extends Order {
  comments: Comment[];
  time_logs: TimeLog[];
  custom_works: CustomWork[];
  custom_parts: CustomPart[];
}

export interface Mechanic {
  id: number;
  name: string;
  email: string;
  phone: string;
  specialty: string;
  telegram_id?: number;
  active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AuthResponse {
  token: string;
  mechanic: Mechanic;
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
}

export interface MechanicStats {
  active_orders: number;
  completed_today: number;
  time_today_minutes: number;
}

export interface MechanicAllTimeStats {
  total_completed: number;
  active_orders: number;
  total_minutes: number;
  avg_order_time: number;
}

export interface TimeHistoryStats {
  total_minutes: number;
  sessions_count: number;
  orders_count: number;
  avg_session: number;
}

export interface TimeHistoryResponse {
  stats: TimeHistoryStats;
  sessions: TimeLog[];
}

export interface GroupedTimeLog {
  date: string;
  sessions: TimeLog[];
  total_minutes: number;
}

export interface Category {
  id: number;
  name_ru: string;
  name_he?: string;
  name_en?: string;
  icon: string;
  sort_order: number;
  created_at: string;
}

export interface Part {
  id: number;
  category_id: number;
  name_ru: string;
  name_he?: string;
  name_en?: string;
  is_common: boolean;
  sort_order: number;
  created_at: string;
}
