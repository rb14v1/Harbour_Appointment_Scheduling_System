import { useState, type FormEvent } from 'react';
import { appointmentTypesApi } from '../api/resources';
import { errorMessage } from '../api/client';
import type { AppointmentType } from '../types';

interface AppointmentTypeFormProps {
  appointmentType?: AppointmentType;
  onSaved: () => void;
  onCancel: () => void;
}

const DURATIONS = [15, 30, 45, 60, 90, 120, 180, 240];

export default function AppointmentTypeForm({ appointmentType, onSaved, onCancel }: AppointmentTypeFormProps) {
  const [form, setForm] = useState({
    name: appointmentType?.name ?? '',
    description: appointmentType?.description ?? '',
    duration_minutes: appointmentType?.duration_minutes ?? 60,
    is_active: appointmentType?.is_active ?? true,
  });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      if (appointmentType) {
        await appointmentTypesApi.update(appointmentType.id, form);
      } else {
        await appointmentTypesApi.create(form);
      }
      onSaved();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="form-grid">
        <label className="field">
          <span>Name</span>
          <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </label>
        <label className="field">
          <span>Duration</span>
          <select
            value={form.duration_minutes}
            onChange={(e) => setForm({ ...form, duration_minutes: Number(e.target.value) })}
          >
            {DURATIONS.map((minutes) => (
              <option key={minutes} value={minutes}>
                {minutes} minutes
              </option>
            ))}
          </select>
        </label>
        <label className="field field-wide">
          <span>Description</span>
          <textarea rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </label>
        <label className="field checkbox">
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
          />
          <span>Active (available for new bookings)</span>
        </label>
      </div>
      {error && <p className="form-error" role="alert">{error}</p>}
      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Saving…' : 'Save type'}
        </button>
      </div>
    </form>
  );
}
