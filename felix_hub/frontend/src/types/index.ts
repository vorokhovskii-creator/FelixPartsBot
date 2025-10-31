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
