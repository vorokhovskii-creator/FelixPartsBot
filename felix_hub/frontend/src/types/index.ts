export interface Order {
  id: number;
  mechanic_name: string;
  vin: string;
  category: string;
  part_name: string;
  part_type: string;
  status: 'новый' | 'в работе' | 'готов' | 'выдан';
  photo_url?: string;
  created_at: string;
  updated_at: string;
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
