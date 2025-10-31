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
  created_at: string;
  updated_at: string;
  total_time_minutes: number;
  comments_count: number;
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
