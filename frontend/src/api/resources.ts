import { request } from './client';
import type {
  Appointment,
  AppointmentCreateInput,
  AppointmentType,
  AppointmentTypeInput,
  AppointmentUpdateInput,
  Customer,
  CustomerInput,
  DashboardData,
} from '../types';

function query(params: Record<string, string | undefined>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) search.set(key, value);
  });
  const text = search.toString();
  return text ? `?${text}` : '';
}

export const customersApi = {
  list: (search = '') => request<Customer[]>('GET', `/customers/${query({ search })}`),
  create: (data: CustomerInput) => request<Customer>('POST', '/customers/', data),
  update: (id: string, data: Partial<CustomerInput>) => request<Customer>('PATCH', `/customers/${id}/`, data),
  remove: (id: string) => request<void>('DELETE', `/customers/${id}/`),
};

export const appointmentTypesApi = {
  list: () => request<AppointmentType[]>('GET', '/appointment-types/'),
  create: (data: AppointmentTypeInput) => request<AppointmentType>('POST', '/appointment-types/', data),
  update: (id: string, data: Partial<AppointmentTypeInput>) =>
    request<AppointmentType>('PATCH', `/appointment-types/${id}/`, data),
  remove: (id: string) => request<void>('DELETE', `/appointment-types/${id}/`),
};

export const appointmentsApi = {
  list: (filters: Record<string, string>) => request<Appointment[]>('GET', `/appointments/${query(filters)}`),
  get: (id: string) => request<Appointment>('GET', `/appointments/${id}/`),
  create: (data: AppointmentCreateInput) => request<Appointment>('POST', '/appointments/', data),
  update: (id: string, data: AppointmentUpdateInput) => request<Appointment>('PATCH', `/appointments/${id}/`, data),
  reschedule: (id: string, data: { start_at: string; end_at: string }) =>
    request<Appointment>('POST', `/appointments/${id}/reschedule/`, data),
  complete: (id: string) => request<Appointment>('POST', `/appointments/${id}/complete/`),
  cancel: (id: string) => request<Appointment>('POST', `/appointments/${id}/cancel/`),
};

export const dashboardApi = {
  get: () => request<DashboardData>('GET', '/dashboard/'),
};
