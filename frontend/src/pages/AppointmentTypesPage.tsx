import { useCallback, useEffect, useState } from 'react';
import { appointmentTypesApi } from '../api/resources';
import { errorMessage } from '../api/client';
import AppointmentTypeForm from '../components/AppointmentTypeForm';
import Modal from '../components/Modal';
import type { AppointmentType } from '../types';

export default function AppointmentTypesPage() {
  const [types, setTypes] = useState<AppointmentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modal, setModal] = useState<{ appointmentType?: AppointmentType } | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setTypes(await appointmentTypesApi.list());
      setError(null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleDelete(appointmentType: AppointmentType) {
    if (!window.confirm(`Delete appointment type "${appointmentType.name}"?`)) return;
    try {
      await appointmentTypesApi.remove(appointmentType.id);
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <section>
      <header className="page-header">
        <h1>Appointment Types</h1>
        <button type="button" className="btn btn-primary" onClick={() => setModal({})}>
          Add type
        </button>
      </header>

      {error && <p className="form-error">{error}</p>}

      <div className="card table-wrap">
        {loading ? (
          <p className="muted">Loading types…</p>
        ) : types.length === 0 ? (
          <p className="muted">No appointment types yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Duration</th>
                <th>Status</th>
                <th>Description</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {types.map((type) => (
                <tr key={type.id}>
                  <td>{type.name}</td>
                  <td>{type.duration_minutes} min</td>
                  <td>{type.is_active ? 'Active' : 'Inactive'}</td>
                  <td>{type.description}</td>
                  <td className="actions">
                    <button
                      type="button"
                      className="btn btn-ghost"
                      onClick={() => setModal({ appointmentType: type })}
                    >
                      Edit
                    </button>
                    <button type="button" className="btn btn-ghost danger" onClick={() => handleDelete(type)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {modal && (
        <Modal title={modal.appointmentType ? 'Edit appointment type' : 'Add appointment type'} onClose={() => setModal(null)}>
          <AppointmentTypeForm
            appointmentType={modal.appointmentType}
            onCancel={() => setModal(null)}
            onSaved={() => {
              setModal(null);
              load();
            }}
          />
        </Modal>
      )}
    </section>
  );
}
