import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { Link, useParams } from 'react-router-dom';
import { appointmentsApi } from '../api/resources';
import { errorMessage } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import type { Appointment } from '../types';
import { formatDateTime, formatTime, fromLocalInputValue, toLocalInputValue } from '../utils/datetime';

export default function AppointmentDetailsPage() {
  const { id = '' } = useParams();
  const [appointment, setAppointment] = useState<Appointment | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [rescheduling, setRescheduling] = useState(false);
  const [newStart, setNewStart] = useState('');
  const [newEnd, setNewEnd] = useState('');

  const load = useCallback(async () => {
    try {
      setAppointment(await appointmentsApi.get(id));
      setError(null);
    } catch (err) {
      setError(errorMessage(err));
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function run(action: () => Promise<Appointment>) {
    setBusy(true);
    setError(null);
    try {
      setAppointment(await action());
      setRescheduling(false);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  function openReschedule() {
    if (!appointment) return;
    setNewStart(toLocalInputValue(appointment.start_at));
    setNewEnd(toLocalInputValue(appointment.end_at));
    setRescheduling(true);
  }

  function handleReschedule(e: FormEvent) {
    e.preventDefault();
    run(() => appointmentsApi.reschedule(id, { start_at: fromLocalInputValue(newStart), end_at: fromLocalInputValue(newEnd) }));
  }

  function handleCancel() {
    if (window.confirm('Cancel this appointment? Its time slot will become available.')) {
      run(() => appointmentsApi.cancel(id));
    }
  }

  if (!appointment) {
    return error ? <p className="form-error">{error}</p> : <p className="muted">Loading appointment…</p>;
  }

  const isScheduled = appointment.status === 'scheduled';

  return (
    <section>
      <header className="page-header">
        <h1>Appointment details</h1>
        <Link to="/appointments" className="btn btn-ghost">
          Back to list
        </Link>
      </header>

      {error && <p className="form-error" role="alert">{error}</p>}

      <div className="card">
        <div className="detail-header">
          <StatusBadge status={appointment.status} />
          <div className="actions">
            {isScheduled && (
              <>
                <Link to={`/appointments/${id}/edit`} className="btn">
                  Edit
                </Link>
                <button type="button" className="btn" onClick={openReschedule} disabled={busy}>
                  Reschedule
                </button>
                <button type="button" className="btn btn-primary" onClick={() => run(() => appointmentsApi.complete(id))} disabled={busy}>
                  Mark completed
                </button>
                <button type="button" className="btn btn-danger" onClick={handleCancel} disabled={busy}>
                  Cancel appointment
                </button>
              </>
            )}
          </div>
        </div>

        <dl className="details">
          <dt>Customer</dt>
          <dd>{appointment.customer_name}</dd>
          <dt>Appointment type</dt>
          <dd>{appointment.appointment_type_name}</dd>
          <dt>Start</dt>
          <dd>{formatDateTime(appointment.start_at)}</dd>
          <dt>End</dt>
          <dd>{formatTime(appointment.end_at)}</dd>
          <dt>Description</dt>
          <dd>{appointment.description || <span className="muted">None</span>}</dd>
          <dt>Created</dt>
          <dd>{formatDateTime(appointment.created_at)}</dd>
          <dt>Last updated</dt>
          <dd>{formatDateTime(appointment.updated_at)}</dd>
        </dl>
      </div>

      {rescheduling && (
        <form className="card form" onSubmit={handleReschedule}>
          <h2>Reschedule</h2>
          <div className="form-grid">
            <label className="field">
              <span>New start</span>
              <input type="datetime-local" step={900} required value={newStart} onChange={(e) => setNewStart(e.target.value)} />
            </label>
            <label className="field">
              <span>New end</span>
              <input type="datetime-local" step={900} required value={newEnd} onChange={(e) => setNewEnd(e.target.value)} />
            </label>
          </div>
          <div className="form-actions">
            <button type="button" className="btn" onClick={() => setRescheduling(false)}>
              Close
            </button>
            <button type="submit" className="btn btn-primary" disabled={busy}>
              Confirm reschedule
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
