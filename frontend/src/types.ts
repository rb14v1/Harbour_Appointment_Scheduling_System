export type AppointmentStatus = 'scheduled' | 'completed' | 'cancelled';

export interface Customer {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  address: string;
  created_at: string;
  updated_at: string;
}

export interface CustomerInput {
  full_name: string;
  email: string;
  phone: string;
  address?: string;
}

export interface AppointmentType {
  id: string;
  name: string;
  description: string;
  duration_minutes: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AppointmentTypeInput {
  name: string;
  description?: string;
  duration_minutes: number;
  is_active?: boolean;
}

export interface Appointment {
  id: string;
  customer_id: string;
  customer_name: string;
  appointment_type_id: string;
  appointment_type_name: string;
  start_at: string;
  end_at: string;
  date: string;
  description: string;
  status: AppointmentStatus;
  created_at: string;
  updated_at: string;
}

export interface AppointmentCreateInput {
  customer_id: string;
  appointment_type_id: string;
  start_at: string;
  end_at: string;
  description?: string;
}

export interface AppointmentUpdateInput {
  customer_id?: string;
  appointment_type_id?: string;
  description?: string;
}

export interface DashboardData {
  total: number;
  today: number;
  upcoming: number;
  completed: number;
  cancelled: number;
  recent: Appointment[];
  by_type: { type_id: string; type_name: string; count: number }[];
}
