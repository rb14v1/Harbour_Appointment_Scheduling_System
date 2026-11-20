import { useEffect, useState, type FormEvent } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { appointmentTypesApi, appointmentsApi, customersApi } from '../api/resources';
import { errorMessage } from '../api/client';
import type { AppointmentStatus, AppointmentType, Customer } from '../types';
import {
  addMinutesToLocalInput,
  fromLocalInputValue,
  toLocalInputValue,
} from '../utils/datetime';

interface FormState {
  customer_id: string;
  appointment_type_id: string;
  start: string;
  end: string;
  description: string;
}

const emptyForm: FormState = { customer_id: '', appointment_type_id: '', start: '', end: '', description: '' };

export default function AppointmentFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(emptyForm);
  const [status, setStatus] = useState<AppointmentStatus>('scheduled');
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [types, setTypes] = useState<AppointmentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const existing = id ? appointmentsApi.get(id) : Promise.resolve(null);
    Promise.all([customersApi.list(), appointmentTypesApi.list(), existing])
      .then(([customerList, typeList, appointment]) => {
        if (!active) return;
        setCustomers(customerList);
        setTypes(typeList.filter((type) => type.is_active || type.id === appointment?.appointment_type_id));
        if (appointment) {
          setStatus(appointment.status);
          setForm({
            customer_id: appointment.customer_id,
            appointment_type_id: appointment.appointment_type_id,
            start: toLocalInputValue(appointment.start_at),
            end: toLocalInputValue(appointment.end_at),
            description: appointment.description,
          });
        }
      })
      .catch((err) => active && setError(errorMessage(err)))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [id]);

  const selectedType = types.find((type) => type.id === form.appointment_type_id);
  const canChangeCustomerAndType = !isEdit || status === 'scheduled';

  function prefillEnd(start: string, typeId: string) {
    const type = types.find((item) => item.id === typeId);
    return type && start ? addMinutesToLocalInput(start, type.duration_minutes) : '';
  }

  function handleStartChange(start: string) {
    setForm((current) => ({
      ...current,
      start,
      end: !isEdit ? prefillEnd(start, current.appointment_type_id) || current.end : current.end,
    }));
  }

  function handleTypeChange(typeId: string) {
    setForm((current) => ({
      ...current,
      appointment_type_id: typeId,
      end: !isEdit ? prefillEnd(current.start, typeId) || current.end : current.end,
    }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      if (isEdit && id) {
        const payload = canChangeCustomerAndType
          ? { customer_id: form.customer_id, appointment_type_id: form.appointment_type_id, description: form.description }
          : { description: form.description };
        const updated = await appointmentsApi.update(id, payload);
        navigate(`/appointments/${updated.id}`);
      } else {
        const created = await appointmentsApi.create({
          customer_id: form.customer_id,
          appointment_type_id: form.appointment_type_id,
          start_at: fromLocalInputValue(form.start),
          end_at: fromLocalInputValue(form.end),
          description: form.description,
        });
        navigate(`/appointments/${created.id}`);
      }
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="muted">Loading…</p>;

  return (
    <section>
      <header className="page-header">
        <h1>{isEdit ? 'Edit appointment' : 'New appointment'}</h1>
        <Link to={isEdit ? `/appointments/${id}` : '/appointments'} className="btn btn-ghost">
          Back
        </Link>
      </header>

      <form className="card form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label className="field">
            <span>Customer</span>
            <select
              required
              disabled={!canChangeCustomerAndType}
              value={form.customer_id}
              onChange={(e) => setForm({ ...form, customer_id: e.target.value })}
            >
              <option value="" disabled>
                Select a customer
              </option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.full_name}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Appointment type</span>
            <select
              required
              disabled={!canChangeCustomerAndType}
              value={form.appointment_type_id}
              onChange={(e) => handleTypeChange(e.target.value)}
            >
              <option value="" disabled>
                Select a type
              </option>
              {types.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name} ({type.duration_minutes} min)
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Start</span>
            <input
              type="datetime-local"
              step={900}
              required
              disabled={isEdit}
              value={form.start}
              onChange={(e) => handleStartChange(e.target.value)}
            />
          </label>

          <label className="field">
            <span>End</span>
            <input
              type="datetime-local"
              step={900}
              required
              disabled={isEdit}
              value={form.end}
              onChange={(e) => setForm({ ...form, end: e.target.value })}
            />
          </label>

          <label className="field field-wide">
            <span>Description</span>
            <textarea
              rows={4}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </label>
        </div>

        {isEdit && (
          <p className="muted">
            Times change from the appointment details page (reschedule).
            {!canChangeCustomerAndType && ' Customer and type are locked because this appointment is not scheduled.'}
          </p>
        )}
        {!isEdit && selectedType && (
          <p className="muted">End time is pre-filled from the type duration. Adjust if needed.</p>
        )}

        {error && <p className="form-error" role="alert">{error}</p>}

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving…' : isEdit ? 'Save changes' : 'Create appointment'}
          </button>
        </div>
      </form>
    </section>
  );
}
