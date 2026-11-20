import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { appointmentTypesApi, appointmentsApi, customersApi } from '../api/resources';
import { errorMessage } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import type { Appointment, AppointmentType, Customer } from '../types';
import { formatDateTime, formatTime } from '../utils/datetime';

const emptyFilters = { date_from: '', date_to: '', customer_id: '', type_id: '', status: '' };

export default function AppointmentsPage() {
  const [filters, setFilters] = useState(emptyFilters);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [types, setTypes] = useState<AppointmentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    customersApi.list().then(setCustomers).catch(() => undefined);
    appointmentTypesApi.list().then(setTypes).catch(() => undefined);
  }, []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    appointmentsApi
      .list(filters)
      .then((result) => {
        if (!active) return;
        setAppointments(result);
        setError(null);
      })
      .catch((err) => active && setError(errorMessage(err)))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [filters]);

  const setFilter = (field: keyof typeof emptyFilters) => (value: string) =>
    setFilters((current) => ({ ...current, [field]: value }));

  return (
    <section>
      <header className="page-header">
        <h1>Appointments</h1>
        <Link to="/appointments/new" className="btn btn-primary">
          New appointment
        </Link>
      </header>

      <div className="filters">
        <label className="field">
          <span>From</span>
          <input type="date" value={filters.date_from} onChange={(e) => setFilter('date_from')(e.target.value)} />
        </label>
        <label className="field">
          <span>To</span>
          <input type="date" value={filters.date_to} onChange={(e) => setFilter('date_to')(e.target.value)} />
        </label>
        <label className="field">
          <span>Customer</span>
          <select value={filters.customer_id} onChange={(e) => setFilter('customer_id')(e.target.value)}>
            <option value="">All customers</option>
            {customers.map((customer) => (
              <option key={customer.id} value={customer.id}>
                {customer.full_name}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Type</span>
          <select value={filters.type_id} onChange={(e) => setFilter('type_id')(e.target.value)}>
            <option value="">All types</option>
            {types.map((type) => (
              <option key={type.id} value={type.id}>
                {type.name}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Status</span>
          <select value={filters.status} onChange={(e) => setFilter('status')(e.target.value)}>
            <option value="">All statuses</option>
            <option value="scheduled">Scheduled</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </label>
        <button type="button" className="btn btn-ghost" onClick={() => setFilters(emptyFilters)}>
          Clear
        </button>
      </div>

      {error && <p className="form-error">{error}</p>}

      <div className="card table-wrap">
        {loading ? (
          <p className="muted">Loading appointments…</p>
        ) : appointments.length === 0 ? (
          <p className="muted">No appointments match these filters.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Start</th>
                <th>End</th>
                <th>Customer</th>
                <th>Type</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {appointments.map((appointment) => (
                <tr key={appointment.id}>
                  <td>
                    <Link to={`/appointments/${appointment.id}`}>{formatDateTime(appointment.start_at)}</Link>
                  </td>
                  <td>{formatTime(appointment.end_at)}</td>
                  <td>{appointment.customer_name}</td>
                  <td>{appointment.appointment_type_name}</td>
                  <td>
                    <StatusBadge status={appointment.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
